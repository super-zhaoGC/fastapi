import bcrypt
from app.core.exception_handler import ServiceError

"""
密码加密工具类
"""
def encrypt_password(password: str) -> str:
    """
    密码加密
    :param password: 密码
    :return: 加密后的密码
    """
    # 对密码进行编码
    password = password.encode("utf-8")
    # 生成盐值
    salt = bcrypt.gensalt(rounds=12)
    # 对密码进行加密
    hashed_password = bcrypt.hashpw(password, salt)
    # 对加密后的密码进行解码
    return hashed_password.decode("utf-8")

def check_password(password: str, hashed_password: str) -> bool:
    """
    校验密码是否正确
    :param password: 用户输入的密码
    :param hashed_password: 数据库中加密后的密码
    :return: 是否正确
    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def get_user_id(current_user:dict):
    """
    从当前用户信息中获取用户ID
    
    注意: 登录时写入 JWT 的用户信息是 camelCase 结构
    {"userId": 1, "user": {"userId": 1, ...}, ...},
    所以这里必须按 "userId" 取值, 而不是 "user_id"。
    
    参数:
        current_user: 当前登录用户的信息字典
    
    返回:
        用户ID
    
    异常:
        ServiceError: 用户ID不存在时抛出
    """
    user = current_user.get("user") or {}  # 嵌套的用户详细信息
    user_id = current_user.get("userId")  # 顶层用户ID(登录 payload 里的键名)
    if user_id is None:  # 顶层没有时回退到嵌套结构
        user_id = user.get("userId")
    if user_id is None:  # 判断user_id是否存在
        raise ServiceError("用户ID不存在")  # 不存在则抛出业务异常
    return user_id  # 返回用户ID