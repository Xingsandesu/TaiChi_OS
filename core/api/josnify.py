import json

from flask import Response

CODE_YES = 200  # 操作成功的响应码
CODE_NO = 400  # 操作失败的响应码
CODE_ERROR = 500  # 服务器错误的响应码
CODE_NOT_FOUND = 404  # 未找到的响应码


def create_api_response(code: int, errmsg: any = '', data: any = None):
    """
    返回一个josnify后的对象
    :param code: 响应码
    :param errmsg: 错误信息
    :param data: 要带上的数据
    :return: josnify()后的对象
    """
    json_data = {
        'code': code,
        'errmsg': errmsg,
        'data': data
    }

    response = Response(json.dumps(json_data, ensure_ascii=False),
                        mimetype="application/json; charset=utf-8")
    return response
