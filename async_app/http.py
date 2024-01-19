import json
import logging
import os
import socket
from subprocess import run

import tornado.httpclient
import tornado.ioloop
import tornado.web
from aiodocker import Docker

from core.config import SOURCE_URL
from core.models import client

CODE_YES = 200  # 操作成功的响应码
CODE_NO = 400  # 操作失败的响应码


def create_api_response(handler: tornado.web.RequestHandler, code: int, errmsg: any = '', data: any = None):
    """
    返回一个josnify后的对象
    :param handler: tornado.web.RequestHandler实例
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

    handler.set_header("Content-Type", "application/json; charset=utf-8")
    handler.write(json_data)
    




class CreateContainerHandler(tornado.web.RequestHandler):
    async def post(self, id):
        aiodocker = Docker()
        base_url = SOURCE_URL
        run_file_url = f"{base_url}/app/{id}/run.json"
        logging.info(f"软件安装run.json文件路径:{run_file_url}")

        http_client = tornado.httpclient.AsyncHTTPClient()
        try:
            response = await http_client.fetch(run_file_url, request_timeout=0.5)
            app_run_data = json.loads(response.body)
        except Exception as e:
            logging.error(f"软件源没有{id}, {e}")
            return create_api_response(self, CODE_NO, f"软件源没有{id}, {e}")
        finally:
            http_client.close()

        image = app_run_data['image']
        name = app_run_data['name']
        ports = app_run_data['ports']
        restart_policy = app_run_data['restart_policy']
        env = app_run_data.get('env', {})  # 获取环境变量
        run_cmd = app_run_data.get('run_cmd', {})

        logging.info(f"Image: {image}")
        logging.info(f"Name: {name}")
        logging.info(f"Ports: {ports}")
        logging.info(f"Restart Policy: {restart_policy}")
        logging.info(f"Environment Variables: {env}")  # 打印环境变量
        
        volumes = app_run_data.get('volumes', {})
        for volume, details in volumes.items():
            if volume not in [v.name for v in client.volumes.list()]:
                logging.info(f"将创建存储卷:{volume}")
                client.volumes.create(volume)
                bind_path = details['bind']
                host_path = f"/var/lib/docker/volumes/{volume}/_data{bind_path}"
                logging.info(f"将初始化存储卷:{volume}")
                if os.path.splitext(bind_path)[1] == '' or bind_path.endswith('/'):
                    os.makedirs(host_path, exist_ok=True)
                    logging.info(f"初始化存储卷:创建目录{host_path}")
                else:
                    os.makedirs(os.path.dirname(host_path), exist_ok=True)
                    open(host_path, 'a').close()  # 创建文件
                    logging.info(f"初始化存储卷:创建文件{host_path}")
            else:
                logging.info(f"存储卷:{volume}已存在，将使用已有的存储卷")

        for volume, cmds in run_cmd.items():
            bind_path = volumes[volume]['bind']
            host_path = f"/var/lib/docker/volumes/{volume}/_data{bind_path}"
            if not os.path.isdir(host_path):
                host_path = os.path.dirname(host_path)
            for cmd in cmds:
                cmd = cmd.replace(volume, host_path)
                logging.info(f"执行命令{cmd}成功:{host_path}")
                exec_result = run(cmd, shell=True, capture_output=True, text=True, cwd=host_path)
                if exec_result.returncode != 0:
                    logging.error(f"执行命令{cmd}失败，错误信息：{exec_result.stderr}")
                    return create_api_response(self, CODE_NO, f"执行命令{cmd}失败，错误信息：{exec_result.stderr}")

        # 如果没有指定标签，就添加 :latest 标签
        if ':' not in image:
            image += ':latest'

        # 首先，检查镜像是否已经存在
        images = await aiodocker.images.list()
        if any(img['RepoTags'][0] == image for img in images):
            logging.info(f"镜像:{image} 已经存在")
        else:
            # 如果镜像不存在，尝试拉取镜像
            max_attempts = 2  # 最大尝试次数
            for attempt in range(max_attempts):
                try:
                    logging.info(f"正在拉取镜像:{image}")
                    await aiodocker.images.pull(image)
                    logging.info(f"成功拉取镜像:{image}")
                    break  # 如果成功拉取镜像，就跳出循环
                except aiodocker.exceptions.DockerError:
                    logging.error(f"无法找到镜像:{image}")
                    if attempt < max_attempts - 1:  # 如果还没有达到最大尝试次数，就继续循环
                        continue
                    else:  # 如果已经达到最大尝试次数，就返回错误信息并停止执行
                        return create_api_response(self, CODE_NO, f"无法找到镜像:{image}")

        # 然后，创建并启动容器
        try:
            container = client.containers.create(
                image,
                name=name,
                ports={k: (None, v) for k, v in ports.items()},
                volumes={f"/var/lib/docker/volumes/{v}/_data{details['bind']}": {'bind': details['bind'],
                                                                                 'mode': details['mode']} for v, details
                         in volumes.items()} if volumes else {},
                restart_policy=restart_policy,
                environment=env  # 添加环境变量
            )
            logging.info(f"镜像:{image}")
            logging.info(f"容器名称:{name}")
            logging.info(f"容器端口:{ports}")
            logging.info(f"容器存储卷:{volumes if volumes else '无'}")
            container.start()
            logging.info(f"容器{name}创建成功")
            return create_api_response(self, CODE_YES, '', f"容器{name}创建成功")
        except Exception as e:
            return create_api_response(self, CODE_NO, f"{e}")
