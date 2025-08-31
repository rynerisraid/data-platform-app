from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

# SQLAlchemy engine for PostgreSQL
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False
)

# FastAPI依赖注入数据库Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db

Base = declarative_base()


