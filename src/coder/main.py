from typing import Annotated, Union

import chainlit as cl
from chainlit.auth import authenticate_user
from chainlit.context import init_http_context
from chainlit.utils import mount_chainlit
from fastapi import FastAPI, Depends, Request
from langchain.chains import LLMChain

from gdocs_router import router as gdocs_router
from kb_router import router as kb_router

app = FastAPI()

app.include_router(router=gdocs_router)
app.include_router(router=kb_router)


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


mount_chainlit(app=app, target="chat.py", path="/")
