import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.modules.user.schema import UpdateProfile
from app.modules.user.service import UserService
from app.utils.common import response_error, response_success, handle_data
from app.utils.security_utils import get_user_id

user_router = APIRouter(dependencies=[Depends(get_current_user)])
user_service = UserService()


@user_router.post("/profile/avatar", summary="更新用户头像")
async def avatar(file: UploadFile = File(...), current_user: dict = Depends(get_current_user),
                 db: AsyncSession = Depends(get_db)):
    """
    更新用户头像
    """
    # 1. 校验上传文件是否为空
    if file is None or not file.filename:
        return response_error("上传文件失败，请重新上传")
    # 2. 获取当前登录用户的ID
    # user_id = current_user.get("userId")
    user_id = get_user_id(current_user)

    # 3. 准备存放头像的文件夹
    upload_dir = Path(settings.fast_profile + "/avatar")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 为上传的文件生成唯一的文件名
    original_filename = file.filename
    extension = ""
    if "." in original_filename:
        extension = original_filename[original_filename.rfind("."):]

    unique_filename = uuid.uuid4().hex + extension

    # 4. 保存上传的文件到指定路径
    file_path = upload_dir / unique_filename
    content = await file.read()
    file_path.write_bytes(content)
    # 5. 构建头像URL
    avatar_url = f"/profile/avatar/{unique_filename}"

    # update_user_avatar 是 async 方法，必须 await：
    # 不 await 得到的是 coroutine 对象，和 int 比较会抛 TypeError，
    # 同时触发 "coroutine was never awaited" 的 RuntimeWarning。
    updated = await user_service.update_user_avatar(user_id, db, avatar_url)
    if updated > 0:
        return response_success(imgUrl=avatar_url)

    return response_error("更新用户头像失败")

@user_router.put("/profile", summary="更新用户个人信息")
async def update_profile(profile_data:UpdateProfile,current_user:dict=Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    """
    更新用户个人信息
    :param profile_data: 更新个人信息的请求体
    :param current_user: 当前登录用户信息
    :param db: 数据库会话
    :return:
    """
    user_id=get_user_id(current_user)
    return handle_data(await user_service.update_profile(user_id,profile_data.user_name,profile_data.sex,db))

