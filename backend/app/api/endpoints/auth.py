from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.security import verify_password, create_access_token
from app.crud import user as user_crud
from app.schemas import user as user_schema

router = APIRouter()


@router.post("/login", response_model=user_schema.TokenResponse)
def login(
    *,
    db: Session = Depends(deps.get_db),
    payload: user_schema.UserLoginRequest,
):
    user = user_crud.get_by_username(db, payload.username)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(
        subject=user.username,
        claims={"uid": user.id, "is_admin": user.is_admin},
    )
    return user_schema.TokenResponse(access_token=token)


@router.get("/me", response_model=user_schema.UserResponse)
def me(current_user=Depends(deps.get_current_user)):
    return current_user


@router.post("/users", response_model=user_schema.UserResponse)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    payload: user_schema.UserCreateRequest,
    current_user=Depends(deps.get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="没有权限创建用户")
    existing = user_crud.get_by_username(db, payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = user_crud.create_user(db, payload.username, payload.password, payload.is_admin)
    return user


@router.get("/users", response_model=user_schema.UserListResponse)
def list_users(
    *,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="没有权限查看用户列表")
    users = user_crud.list_users(db)
    return user_schema.UserListResponse(items=users)


@router.delete("/users/{user_id}")
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user=Depends(deps.get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="没有权限删除用户")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="不能删除当前登录账号")
    ok = user_crud.delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"message": "删除成功"}
