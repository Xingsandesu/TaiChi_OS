import logging
import os
import requests
from flask import Blueprint, render_template, request
from flask_login import login_required

from core.config import HOME_PATH, SOURCE_URL
from core.models import items, listdir, get_m_time, get_levels, get_abs_path, update_docker

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
    response = requests.get(SOURCE_URL + '/app.json')
    logging.info(response.text)  # 打印响应内容
    try:
        apps = response.json()
    except json.JSONDecodeError:
        logging.error("解析JSON时出错")
        apps = {}
    return render_template('install.html', apps=apps)


@bp.route('/containers')  # /containers
@login_required
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
