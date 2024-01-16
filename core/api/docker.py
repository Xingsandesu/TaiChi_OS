from flask_login import login_required

from core.api.blueprint import bp
from core.api.josnify import create_api_response, CODE_YES, CODE_NO
from core.models import client


############## 容器操作 ##############
# 获取所有容器的列表
@bp.route('/containers', methods=['GET'])
@login_required
def get_containers():
    containers = client.containers.list(all=True)
    return create_api_response(CODE_YES, '', [container.attrs for container in containers])


# 删除一个容器
# noinspection PyShadowingBuiltins
@bp.route('/containers/<id>/delete', methods=['DELETE'])
@login_required
def delete_container(id: str):
    try:
        container = client.containers.get(id)
        container.remove(force=True)
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))


# 停止一个容器
# noinspection PyShadowingBuiltins
@bp.route('/containers/<id>/stop', methods=['POST'])
@login_required
def stop_container(id: str):
    try:
        container = client.containers.get(id)
        container.stop(timeout=0)
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))


# 启动一个容器
# noinspection PyShadowingBuiltins
@bp.route('/containers/<id>/start', methods=['POST'])
@login_required
def start_container(id: str):
    try:
        container = client.containers.get(id)
        container.start()
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))


# 停止并删除一个容器
# noinspection PyShadowingBuiltins
@bp.route('/containers/<id>/stop_and_delete', methods=['DELETE'])
@login_required
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
@login_required
def get_images():
    images = client.images.list()
    return create_api_response(CODE_YES, '', [image.attrs for image in images])


# 删除一个镜像
# noinspection PyShadowingBuiltins
@bp.route('/images/<id>/delete', methods=['DELETE'])
@login_required
def delete_image(id: str):
    try:
        client.images.remove(id)
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))


############## 镜像操作结束 ##############

############## 存储卷操作 ##############
# 获取所有存储卷的列表
@bp.route('/volumes', methods=['GET'])
@login_required
def get_volumes():
    try:
        volumes = client.volumes.list()
        return create_api_response(CODE_YES, '', [volume.attrs for volume in volumes])
    except Exception as e:
        return create_api_response(CODE_NO, str(e))


# noinspection PyShadowingBuiltins
@bp.route('/volumes/<id>/delete', methods=['DELETE'])
@login_required
def delete_volume(id: str):
    try:
        volume = client.volumes.get(id)
        volume.remove(force=True)
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))
############## 存储卷操作结束 ##############
