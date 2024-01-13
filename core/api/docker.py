import logging

import requests

from core.api.blueprint import bp
from core.api.josnify import create_api_response, CODE_YES, CODE_NO
from core.models import client


############## 容器操作 ##############
# 获取所有容器的列表
@bp.route('/containers', methods=['GET'])
def get_containers():
    containers = client.containers.list(all=True)
    return create_api_response(CODE_YES, '', [container.attrs for container in containers])


# 软件安装
# noinspection PyShadowingBuiltins
@bp.route('/containers/<id>/create', methods=['POST'])
def create_container(id: str):
    # 1. 定义软件源的域名
    base_url = "https://app.kookoo.top"
    run_file_url = f"{base_url}/app/{id}/run.json"
    logging.info(f"软件安装run.json文件路径:{run_file_url}")

    # 2. 获取run.json文件内容
    try:
        run_file_response = requests.get(run_file_url)
        app_run_data = run_file_response.json()
    except Exception as e:
        logging.error(f"软件源没有{id}, {e}")
        return create_api_response(CODE_NO, f"软件源没有{id}")
    image = app_run_data['image']
    name = app_run_data['name']
    ports = app_run_data['ports']
    restart_policy = app_run_data['restart_policy']

    # 打印提取的键值对
    logging.info(f"Image: {image}")
    logging.info(f"Name: {name}")
    logging.info(f"Ports: {ports}")
    logging.info(f"Restart Policy: {restart_policy}")

    # 3. 检查端口冲突
    if client.containers.list(filters={'expose': list(ports.keys())}):
        logging.error(f"端口{ports}已被占用")
        return create_api_response(CODE_NO, f"端口{ports}已被占用")

    # 4. 检查并创建存储卷
    volumes = app_run_data.get('volumes', {})
    for volume in volumes.keys():
        if volume not in [v.name for v in client.volumes.list()]:
            logging.info(f"将创建存储卷:{volume}")
            client.volumes.create(volume)
        else:
            logging.info(f"存储卷:{volume}已存在，将使用已有的存储卷")

    # 5. 使用docker SDK创建并启动容器
    # 首先，尝试拉取镜像
    try:
        logging.info(f"正在拉取镜像:{image}")
        client.images.pull(image)
        logging.info(f"成功拉取镜像:{image}")
    except docker.errors.ImageNotFound:
        logging.error(f"无法找到镜像:{image}")
        return create_api_response(CODE_NO, f"无法找到镜像:{image}")

    # 然后，创建并启动容器
    container = client.containers.create(
        image,
        name=name,
        ports={k: (None, v) for k, v in ports.items()},
        volumes={v['bind']: {'bind': v['bind'], 'mode': v['mode']} for v in volumes.values()} if volumes else {},
        restart_policy=restart_policy
    )
    logging.info(f"镜像:{image}")
    logging.info(f"容器名称:{name}")
    logging.info(f"容器端口:{ports}")
    logging.info(f"容器存储卷:{volumes if volumes else '无'}")
    container.start()
    logging.info(f"容器{name}创建成功")

    return create_api_response(CODE_YES, '', f"容器{name}创建成功")


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
# noinspection PyShadowingBuiltins
@bp.route('/containers/<id>/start', methods=['POST'])
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

############## 存储卷操作 ##############
# 获取所有存储卷的列表
@bp.route('/volumes', methods=['GET'])
def get_volumes():
    try:
        volumes = client.volumes.list()
        return create_api_response(CODE_YES, '', [volume.attrs for volume in volumes])
    except Exception as e:
        return create_api_response(CODE_NO, str(e))


# noinspection PyShadowingBuiltins
@bp.route('/volumes/<id>/delete', methods=['DELETE'])
def delete_volume(id: str):
    try:
        volume = client.volumes.get(id)
        volume.remove(force=True)
        return create_api_response(CODE_YES, '', {'result': 'success'})
    except Exception as e:
        return create_api_response(CODE_NO, str(e))
############## 存储卷操作结束 ##############
