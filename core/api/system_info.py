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


'''
旧的系统资源 API
@stats_blueprint_GET.route('/stats', methods=['GET'])
def get_stats():
    """
    获取系统状态 API (GET)
    示例返回值
    {
    "cpu_usage": 0.8,
    "disk_usage": 31.3,
    "download_speed": 140.9511255761284,
    "memory_usage": 30.4,
    "system_version": "Windows-10-10.0.22621-SP0",
    "upload_speed": 78.30618087562688
    }
    """
    # 创建一个字典来存储prev_net_info和prev_time
    prev_stats = getattr(get_stats, 'prev_stats', None)

    # 获取CPU使用率
    cpu_usage = psutil.cpu_percent(interval=1)

    # 获取内存使用率
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent

    # 获取磁盘使用率
    disk_info = psutil.disk_usage('/')
    disk_usage = disk_info.percent

    # 获取网络上传和下载数据量
    net_info = psutil.net_io_counters()
    bytes_sent = net_info.bytes_sent
    bytes_recv = net_info.bytes_recv

    # 计算网络速度
    if prev_stats is not None:
        elapsed_time = time.time() - prev_stats['prev_time']
        upload_speed = (bytes_sent - prev_stats['prev_net_info'].bytes_sent) / elapsed_time
        download_speed = (bytes_recv - prev_stats['prev_net_info'].bytes_recv) / elapsed_time
    else:
        upload_speed = download_speed = 0

    # 更新prev_stats
    get_stats.prev_stats = {'prev_net_info': net_info, 'prev_time': time.time()}

    # 获取系统版本
    system_version = platform.platform()

    return jsonify(cpu_usage=cpu_usage, memory_usage=memory_usage, disk_usage=disk_usage, upload_speed=upload_speed,
                   download_speed=download_speed, system_version=system_version)
'''
