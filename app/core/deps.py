from fastapi import Header, HTTPException
from app.core import token_service


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    token = token_service.get_token(authorization)

    login_user = token_service.get_login_user(token)
    if not login_user:
        raise HTTPException(status_code=401, detail="未登录，请先登录后访问")

    if not token_service.verify_token(login_user):
        raise HTTPException(status_code=401, detail="登录过期，请重新登录")
    return login_user
