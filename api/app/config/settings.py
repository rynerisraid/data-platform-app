from pydantic_settings import BaseSettings
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer


class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = ""
    ASYNC_DATABASE_URL: str = ""
    DATASOURCE_KEY: str = ""

    # 认证配置
    NEXTAUTH_SECRET: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"



settings = Settings()



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
