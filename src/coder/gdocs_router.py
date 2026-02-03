from typing import Annotated, Union

import chainlit as cl
from chainlit.auth import get_current_user
from chainlit.context import init_http_context
from fastapi import Depends, Request, Query, APIRouter
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from starlette.config import environ

from gdoc_service import list_all_gdocs, gdoc_content_by_id
from vector_stores import create_chroma

embeddings = OpenAIEmbeddings(base_url=environ.get("OPENAI_API_URL"))

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
router = APIRouter(
    prefix="/gdocs",
    tags=["googledocs"]
)


@router.get("/")
async def list_docs(
        current_user: Annotated[
            Union[cl.User], Depends(get_current_user)
        ],
        page_token: Annotated[str | None, Query(alias="pageToken")] = None,
        page_size: Annotated[int, Query(alias="pageSize")] = 10,
):
    init_http_context(user=current_user)
    token = current_user.metadata.get('token')
    items, next_page_token = await list_all_gdocs(token, page_size, page_token)
    resp = {'documents': [map_item(it) for it in items], 'next_page_token': next_page_token}
    print('response: ', resp)
    return resp


@router.get("/{doc_id}")
async def upload_doc(
        doc_id: str,
        current_user: Annotated[
            Union[cl.User], Depends(get_current_user)
        ],
):
    init_http_context(user=current_user)
    token = current_user.metadata.get('token')
    texts, metadatas = await load_doc(doc_id, token)
    identifier = current_user.identifier
    user_id = current_user.to_dict().get('id')
    db = create_chroma(embeddings, texts, metadatas, user_id + '-docs')
    # db_records = db.get()
    # print(db_records['documents'])
    return "ok"


@router.post("/save")
async def upload_docs(
        request: Request,
        current_user: Annotated[
            Union[cl.User], Depends(get_current_user)
        ],
):
    init_http_context(user=current_user)
    token = current_user.metadata.get('token')
    data = await request.json()
    texts = []
    metadatas = []
    for item in data:
        doc_id = item["id"]
        t, m = await load_doc(doc_id, token)
        # or we can use Chroma.add_text
        texts.extend(t)
        metadatas.extend(m)
    user_id = current_user.to_dict().get('id')
    _ = await cl.make_async(create_chroma)(embeddings, texts, metadatas, user_id)
    return {"message": "Данные успешно сохранены"}


def map_item(item):
    return {'name': item['name'], 'id': item['id'], 'is_enabled': False}


async def load_doc(doc_id: str, token: str) -> (list[str], list[dict[str, str]]):
    full_text = await gdoc_content_by_id(token, doc_id)
    texts = text_splitter.split_text(full_text)
    # and metadata for each chunk
    metadatas = [{"source": f"{i}-pl"} for i in range(len(texts))]
    return texts, metadatas
