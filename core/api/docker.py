from core.models import client

from .blueprint import bp
from .josnify import create_api_response, CODE_YES, CODE_NO


# 获取所有容器的列表
@bp.route('/containers', methods=['GET'])
def get_containers():
    containers = client.containers.list(all=True)
    return create_api_response(CODE_YES, '', [container.attrs for container in containers])


# 获取所有镜像的列表
@bp.route('/images', methods=['GET'])
def get_images():
    images = client.images.list()
    return create_api_response(CODE_YES, '', [image.attrs for image in images])


# 创建一个新的容器
@bp.route('/containers/create', methods=['POST'])
def create_container():
    container = client.containers.create('ubuntu', 'echo hello world')
    return create_api_response(CODE_YES, '', {'id': container.short_id})


# 删除一个容器
# noinspection PyShadowingBuiltins
@bp.route('/containers/<id>/delete', methods=['DELETE'])
def delete_container(id):
    try:
        container = client.containers.get(id)
        container.remove()
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))


# 删除一个镜像
# noinspection PyShadowingBuiltins
@bp.route('/images/<id>/delete', methods=['DELETE'])
def delete_image(id):
    try:
        client.images.remove(id)
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))


# 停止一个容器
# noinspection PyShadowingBuiltins
@bp.route('/containers/<id>/stop', methods=['POST'])
def stop_container(id):
    try:
        container = client.containers.get(id)
        container.stop()
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))


# 获取一个容器的日志
# noinspection PyShadowingBuiltins
@bp.route('/containers/<id>/logs', methods=['GET'])
def get_logs(id):
    try:
        container = client.containers.get(id)
        logs = container.logs()
        return create_api_response(CODE_YES, '', {'logs': logs.decode('utf-8')})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))
