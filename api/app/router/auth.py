# -------------------- Imports --------------------
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.auth import User, UserCreate, UserRead
from app.config.db import get_db
from app.services.auth import AuthService
from pydantic import BaseModel
from app.utils.schema import BaseResponse

router = APIRouter()

# -------------------- Pydantic Schemas --------------------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class ResetPasswordRequest(BaseModel):
    username: str
    new_password: str


# 创建 AuthService 实例
auth_service = AuthService()

# -------------------- Routes --------------------
@router.post("/register", response_model=BaseResponse[UserRead])
def register(user: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(user, db)

@router.post("/token", response_model=Token) #BaseResponse[Token]
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer") #BaseResponse[Token](data=Token(access_token=access_token, token_type="bearer"))

@router.get("/me", response_model=BaseResponse[UserRead])
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    获取当前用户信息
    """
    return BaseResponse[UserRead](data=current_user)

@router.post("/reset-password", response_model=BaseResponse[dict])
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = auth_service.get_user_by_username(db, req.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = auth_service.get_password_hash(req.new_password)
    db.commit()
    return BaseResponse[dict](data={"msg": "Password reset successful"})



# 前端
@router.post("/front_token", response_model=BaseResponse[Token])
def front_login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(data={"sub": user.username})
    return BaseResponse[Token](data=Token(access_token=access_token, token_type="bearer"))
