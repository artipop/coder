from typing import Annotated, Union

import chainlit as cl
from chainlit.auth import authenticate_user
from chainlit.context import init_http_context
from chainlit.utils import mount_chainlit
from fastapi import FastAPI, Depends, Request
from langchain.chains import LLMChain
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from starlette.config import environ

from gdoc_service import list_all_gdocs, gdoc_content_by_id
from vector_stores import create_chroma

app = FastAPI()
embeddings = OpenAIEmbeddings(base_url=environ.get("OPENAI_API_URL"))

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)


def map_item(item):
    return {'name': item['name'], 'id': item['id'], 'is_enabled': False}


@app.get("/{thread_id}/gdocs")
async def list_docs(
        request: Request,
        thread_id: str,
        current_user: Annotated[
            Union[cl.User], Depends(authenticate_user)
        ],
):
    print('chat ' + thread_id)
    init_http_context(user=current_user)
    token = current_user.metadata.get('token')


@app.get("/gdocs")
async def list_docs(
        current_user: Annotated[
            Union[cl.User], Depends(authenticate_user)
        ],
        pageToken: str | None = None,
        pageSize: int = 10,
):
    init_http_context(user=current_user)
    token = current_user.metadata.get('token')
    items, nextPageToken = await list_all_gdocs(token, pageSize, pageToken)
    resp = {'documents': [map_item(it) for it in items], 'nextPageToken': nextPageToken}
    print('response: ', resp)
    return resp


@app.get("/gdocs/{doc_id}")
async def upload_doc(
        doc_id: str,
        current_user: Annotated[
            Union[cl.User], Depends(authenticate_user)
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


@app.post("/gdocs/save")
async def upload_docs(
        request: Request,
        current_user: Annotated[
            Union[cl.User], Depends(authenticate_user)
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


async def load_doc(doc_id: str, token: str) -> (list[str], list[dict[str, str]]):
    full_text = await gdoc_content_by_id(doc_id, token)
    texts = text_splitter.split_text(full_text)
    # and metadata for each chunk
    metadatas = [{"source": f"{i}-pl"} for i in range(len(texts))]
    return texts, metadatas


mount_chainlit(app=app, target="chat.py", path="/")
