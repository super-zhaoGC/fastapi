"""
操作消息响应（统一响应格式）
作用：规定所有接口统一返回（code,msg,data）
"""

def response_success(msg:str="操作成功",data=None,**extra)->dict:
    """
    成功响应
    :param msg: 返回消息
    :param data: 返回数据（没有数据，不会出现在响应中）
    :param extra: 额外顶层字段（比如登录接口需要额外返回的token）
    :return:
    """

    result={
        "code":200,
        "msg":msg,
    }
    if data is not None:
        result["data"]=data
    # 额外字段平铺到顶层
    result.update(extra)

    return result

def response_error(msg:str="操作失败",code:int=500)->dict:
    return {"code":code,"msg":msg}

def handle_db(rows:int)->dict:
    """
      根据受影响的行数判断操作是否成功
      :param rows:  数据库操作影响的行数
      """
    return response_success() if rows>0 else response_error()