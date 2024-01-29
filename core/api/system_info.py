# 本文件 GET 请求的系统资源 API 可能会被弃用！！！
# index.js 轮询获取系统资源后端
# 查询cpu、内存、网络的使用情况已弃用，改为使用websocket实时获取
import platform

import psutil
from flask_login import login_required

from core.api.blueprint import bp
from core.api.josnify import create_api_response, CODE_YES


@bp.route('/info', methods=['GET'])
@login_required
def get_stats():
    """
    获取系统状态 API (GET)
    示例返回值
    {
    "code": 200,
    "errmsg": "",
    "data": {
        "disk_usage": 31.3,
        "system_version": "Windows-10-10.0.22621-SP0",
    }
    }
    """

    # 获取磁盘使用率
    disk_info = psutil.disk_usage('/')
    disk_usage = disk_info.percent

    # 获取系统版本
    system_version = platform.platform()

    return create_api_response(CODE_YES, '', {'disk_usage': disk_usage, 'system_version': system_version})

