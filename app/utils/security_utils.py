import bcrypt
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

