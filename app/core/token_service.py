import json
import time
import jwt


from app.core.config import settings


def create_token(login_user:dict)->str:
    """
    根据登录用户信息生成 JWT 令牌

    会在传入字典中嵌入以下字段(单位均为毫秒):
        - loginTime: 当前 Unix 时间戳(秒) * 1000
        - expirationTime: 过期时间戳(秒) * 1000

    参数:
        login_user: 登录用户信息字典, 函数内部会直接修改该字典
    返回:
        JWT 令牌字符串
    """
    # 获取当前 Unix 时间戳(单位: 秒)
    now = int(time.time() * 1000)
    # 计算过期时间 = 当前时间 + token_expire_time(分钟) * 60 * 1000 (转毫秒)
    expiration_time=now+settings.token_expire_time*60*1000

    # 将登录时间和过期时间写入用户字典(注意: loginTime 单位为秒, expirationTime 单位为毫秒)
    login_user["loginTime"]=now
    login_user["expirationTime"]=expiration_time

    # 将用户信息整体序列化为 JSON 字符串, 作为 JWT claims 的 user_key 字段
    claims={"user_key":json.dumps(login_user,ensure_ascii=False)}
    # 使用 HS256 算法和配置的密钥对 claims 进行签名, 生成 JWT 令牌
    return jwt.encode(claims,settings.token_secret,algorithm="HS256")


def parse_token(token:str)->dict|None:
    """
    解析并校验 JWT 令牌

    使用 HS256 算法和配置的密钥解码令牌, 验证签名和有效期。
    令牌无效(如签名错误/已过期)时捕获异常并返回 None。

    参数:
        token: JWT 令牌字符串
    返回:
        解码后的 claims 字典, 解码失败返回 None
    """
    try:
        return jwt.decode(token,settings.token_secret,algorithms=["HS256"])
    except jwt.PyJWKError:
        return None


def get_login_user(token:str)->dict|None:
    """
    从 JWT 令牌中提取登录用户信息

    流程:
        1. 解析令牌得到 claims
        2. 从 claims["user_key"] 中提取 JSON 字符串
        3. 将 JSON 反序列化为用户信息字典

    参数:
        token: JWT 令牌字符串
    返回:
        登录用户信息字典, 令牌无效或 user_key 缺失时返回 None
    """
    if not token:
        return None

    claims=parse_token(token)
    if claims is None:
        return None

    user_json=claims.get("user_key")
    if not user_json:
        return None
    return json.loads(user_json)


def verify_token(login_user:dict)->bool:
    """
    校验登录用户信息是否已过期

    判断 login_user["expirationTime"] 是否大于当前时间(毫秒)。
    注意: create_token 中 expirationTime 的单位为秒 * 1000,
    而 time.time() 返回秒, 故此处乘以 1000 保持单位一致。

    参数:
        login_user: 包含 expirationTime 字段的用户信息字典
    返回:
        未过期返回 True, 已过期或字段缺失返回 False
    """
    return login_user.get("expirationTime",0)>int(time.time()*1000)


def get_token(authorization:str|None)->str|None:
    """
    从 Authorization header 中提取 Bearer 令牌

    支持两种格式:
        - "Bearer <token>" -> 返回 <token>
        - "<token>" (直接是 token) -> 原样返回

    参数:
        authorization: Authorization 头的值, 通常为 "Bearer xxx" 格式
    返回:
        提取出的 token 字符串, header 为空或 None 时返回 None
    """
    if not authorization:
        return None
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization