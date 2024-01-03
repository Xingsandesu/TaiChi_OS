import os
import time
from os.path import join, isdir, abspath, pardir, basename, getmtime

from flask import Blueprint, render_template, request
from flask_login import login_required

from core.config import items_dict, index_title, HOME_PATH


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


bp = Blueprint('index', __name__, url_prefix='/')


@bp.route('/')  # /
@login_required
def index():
    return render_template('index.html', items_dict=items_dict, title=index_title)


@bp.route('/None')  # /about
@login_required
def None_back():
    return render_template('index.html', items_dict=items_dict, title=index_title)


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
