import os
import time
from os.path import join, isdir, abspath, pardir, basename, getmtime

from docker import DockerClient
from flask import Blueprint, render_template, request
from flask_login import login_required

from core.config import items, HOME_PATH, DEFAULT_LOGO_PATH, DOCKER_CATEGORY, app_logo_mapping


# noinspection PyShadowingBuiltins,PyShadowingNames
def listdir(dir):
    """遍历dir文件夹，返回目录列表和文件列表"""
    dirs = []
    files = []
    for item in os.listdir(dir):
        full_name = join(dir, item)
        if isdir(full_name):
            dirs.append(item)
        else:
            files.append(item)

    return dirs, files


def get_m_time(start, paths):
    """
    获取文件或目录的创建时间
    :param start:  起始目录
    :param paths:  文件或目录的名字的列表
    :return:  返回包含元组(path, m_time)类型的列表
    """
    lst = []
    for path in paths:
        full_path = join(start, path)
        m_time = getmtime(full_path)
        lst.append((path, time.asctime(time.localtime(m_time))))

    return lst


def get_levels(start, path):
    """
    获取path每一层的路径, 以start为起始目录 (应确保path在start下)
    :param start: 根目录绝对路径
    :param path: 路径绝对路径
    :return: 包含每层目录的绝对路径的列表
    """

    levels = []
    full_path = path
    base_name = basename(full_path)
    levels.append((full_path, base_name))
    while full_path != start:
        full_path = abspath(join(full_path, pardir))  # 移动到父目录
        base_name = basename(full_path)
        levels.append((full_path, base_name))

    return levels[:: -1]  # 返回反转后的列表


def get_abs_path(start, path):
    """
    获取path的绝对路径,
    :param start: 根目录
    :param path: 相对路径
    :return: 如果path不在start下返回None， 反之返回其绝对路径
    """
    if start and path:
        # start 和 path 都不能为空
        start = abspath(start)
        path = path.lstrip('/')  # 移除路径开头的所有斜杠
        abs_path = abspath(join(start, path))  # 将路径解析为相对于start的绝对路径
        if abs_path.startswith(start):
            return abs_path
    return None


# 定义一个函数，根据应用名称获取对应的logo路径
def get_logo_path(app_name):
    # 从app_logo_mapping字典中获取应用名称对应的logo路径，如果没有找到，则返回默认的logo路径
    return app_logo_mapping.get(app_name, DEFAULT_LOGO_PATH)


# 定义一个函数，获取Docker容器的信息
def get_docker_info(container):
    # 获取容器的名称
    app_name = container.name
    # 获取容器的端口信息
    ports = container.ports
    # 获取映射的端口信息
    mapped_ports = [port_info[0]['HostPort'] for port_info in ports.values() if port_info]
    # 获取应用的logo路径
    logo_path = get_logo_path(app_name)
    # 获取访问者的IP地址
    server_ip = request.host.split(':')[0]
    # 构造基础链接
    base_link = f'http://{server_ip}'
    # 如果有映射的端口，链接中加入端口信息，否则只使用基础链接
    link = f'{base_link}:{mapped_ports[0]}' if mapped_ports else base_link
    # 返回一个字典，包含应用名称、链接和logo路径
    return {'title': app_name, 'link': link, 'logo': logo_path}


# 定义一个函数，更新Docker信息
def update_docker():
    # 从环境变量中创建一个Docker客户端
    client = DockerClient.from_env()
    # 列出所有的Docker容器
    dockers = client.containers.list()
    # 获取所有容器的信息
    existing_items = [get_docker_info(container) for container in dockers]
    # 如果Docker类别不在items字典中，添加该类别和对应的容器信息
    if DOCKER_CATEGORY not in items.items_dict:
        items.add_category(DOCKER_CATEGORY, existing_items)
    else:
        # 如果Docker类别已经存在，对于每一个容器信息，如果它不在类别中，就添加进去
        for item in existing_items:
            if not items.item_exists_in_category(DOCKER_CATEGORY, item):
                items.add_item_to_category(DOCKER_CATEGORY, item)
        # 移除类别中已经不存在的容器信息
        items.remove_nonexistent_items(DOCKER_CATEGORY, existing_items)


bp = Blueprint('index', __name__, url_prefix='/')


@bp.route('/')  # /
@login_required
def index():
    update_docker()
    return render_template('index.html', items_dict=items.items_dict)


@bp.route('/None')  # /about
@login_required
def none_back():
    update_docker()
    return render_template('index.html', items_dict=items.items_dict)


@bp.route('/install')  # /install
@login_required
def install():
    return render_template('install.html')


@bp.route('/containers')  # /containers
def containers():
    return render_template('containers.html')


@bp.route("/monitor")  # /monitor
@login_required
def monitor():
    return render_template("monitor.html")


@bp.route('/files')  # /files
@login_required
def files():
    """首页处理试图函数"""
    path = request.args.get('path') or HOME_PATH  # 若是path为None则f_get_abs_path也为None那么就会一直重定向
    try:
        abs_path = get_abs_path(HOME_PATH, path)  # 获取绝对路径
        if abs_path and os.path.isdir(abs_path):
            # noinspection PyShadowingNames
            dirs, files = listdir(abs_path)
            levels = get_levels(HOME_PATH, abs_path)
            context = {
                'path': abs_path,
                'levels': levels,
                'dirs': get_m_time(abs_path, dirs),
                'files': get_m_time(abs_path, files)
            }
            return render_template('files.html', **context)
        else:
            raise Exception()  # 让外面捕捉异常来跳转页面
    except Exception as e:
        return str(e), 500
