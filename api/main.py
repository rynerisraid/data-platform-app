from fastapi import FastAPI
from app.router import auth as auth_router
from app.router import resources as resources_router
from app.router import workspace as workspace_router
from typing import Union
from app.config.settings import settings
from app.config.db import engine,Base
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

# -------------------- CORS --------------------
from fastapi.middleware.cors import CORSMiddleware
# 前端部署域名，生产环境请改为具体地址，例如 ["https://app.example.com"]
origins = ["*"]

# -------------------- DB --------------------
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

# 添加 CORS 中间件，解决跨域请求问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(resources_router.router, prefix="/resources", tags=["resources"])
app.include_router(workspace_router.router, prefix="/workspace", tags=["workspace"])

@app.get("/")
def read_root():
    return {
        "Hello": "World"
    }

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}