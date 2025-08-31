from fastapi import FastAPI
from app.router import auth, resources, workspace
from app.router.metadata import router as metadata_router
from typing import Union
from app.config.settings import settings
from app.config.db import engine, Base
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

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION
)

# 添加 CORS 中间件，解决跨域请求问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(resources.router, prefix="/resources", tags=["resources"])
app.include_router(workspace.router, prefix="/workspaces", tags=["workspace"])
app.include_router(metadata_router, prefix="/resources", tags=["metadata"])

@app.get("/")
async def root():
    return {"message": "Welcome to Data Platform API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)