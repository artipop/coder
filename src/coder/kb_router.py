from typing import Annotated, Union

import chainlit as cl
from chainlit.auth import get_current_user
from fastapi import Depends, Request, APIRouter
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from starlette.config import environ

from vector_stores import create_chroma

embeddings = OpenAIEmbeddings(base_url=environ.get("OPENAI_API_URL"))

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
router = APIRouter(
    prefix="/kb",
    tags=["knowledgebase"],
)


@router.post("/save")
async def upload_doc(
        request: Request,
        current_user: Annotated[
            Union[cl.User], Depends(get_current_user)
        ],
):
    data = await request.json()
    text_content = data["textContent"]
    url = data["url"]
    texts = text_splitter.split_text(text_content)
    # and metadata for each chunk
    metadatas = [{"source": url}]
    user_id = current_user.to_dict().get('id')
    _ = await cl.make_async(create_chroma)(embeddings, texts, metadatas, user_id)
    return {"message": "Данные успешно сохранены"}
