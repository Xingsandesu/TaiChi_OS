from core.api.blueprint import bp
from core.api.josnify import create_api_response, CODE_YES, CODE_NO
from core.models import client


############## 容器操作 ##############
# 获取所有容器的列表
@bp.route('/containers', methods=['GET'])
def get_containers():
    containers = client.containers.list(all=True)
    return create_api_response(CODE_YES, '', [container.attrs for container in containers])


# 创建一个新的容器
@bp.route('/containers/create', methods=['POST'])
def create_container():
    container = client.containers.create('ubuntu', 'echo hello world')
    return create_api_response(CODE_YES, '', {'id': container.short_id})


# 删除一个容器
# noinspection PyShadowingBuiltins
@bp.route('/containers/<id>/delete', methods=['DELETE'])
def delete_container(id: str):
    try:
        container = client.containers.get(id)
        container.remove()
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))


# 停止一个容器
# noinspection PyShadowingBuiltins
@bp.route('/containers/<id>/stop', methods=['POST'])
def stop_container(id: str):
    try:
        container = client.containers.get(id)
        container.stop(timeout=0)
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))


# 启动一个容器
@bp.route('/containers/<id>/start', methods=['POST'])
def start_container(id: str):
    try:
        container = client.containers.get(id)
        container.start()
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))


# 停止并删除一个容器
@bp.route('/containers/<id>/stop_and_delete', methods=['DELETE'])
def stop_and_delete_container(id: str):
    try:
        container = client.containers.get(id)
        container.stop(timeout=0)
        container.remove()
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))


############## 容器操作结束 ##############

############## 镜像操作 ##############
# 获取所有镜像的列表
@bp.route('/images', methods=['GET'])
def get_images():
    images = client.images.list()
    return create_api_response(CODE_YES, '', [image.attrs for image in images])


# 删除一个镜像
# noinspection PyShadowingBuiltins
@bp.route('/images/<id>/delete', methods=['DELETE'])
def delete_image(id: str):
    try:
        client.images.remove(id)
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))

############## 镜像操作结束 ##############
