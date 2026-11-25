from fastapi import APIRouter,Depends
from app.core.logger import logger
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.user.model import User
from app.schemas.common import response_success

home_router = APIRouter()

@home_router.get("/")
def home():
    logger.info("Hello World")
    return {"message": "Hello World"}

@home_router.get("/testdb")
async def testdb(db:AsyncSession=Depends(get_db)):
    """测试数据库连接"""
    statement=select(User).order_by(User.user_id)
    result=await db.execute(statement)
    # select(User) 返回的是 ORM 实体，必须用 scalars() 取出实体；
    # 直接迭代 Result 拿到的是 Row（每行里包一个 User），访问 u.user_name 会报 AttributeError
    users=result.scalars().all()
    return response_success(data=[u for u in users])
