import logging
import mimetypes
import os
import shutil
from os.path import exists, isfile, dirname, join, isdir, basename

import chardet
from flask import request, send_file
from flask_login import login_required

from core.api.blueprint import bp
from core.api.josnify import create_api_response, CODE_YES, CODE_NO
from core.config import HOME_PATH
from core.models import listdir, get_abs_path


@bp.route('/remove/', methods=['POST'])
@login_required
def api_remove():
    """删除文件或目录的api"""

    # path: 文件或目录的路径
    path = request.form.get('path') or HOME_PATH  # 若为空则让后面的if判断失败(不能删除管理的根目录)

    abs_path = get_abs_path(HOME_PATH, path)

    try:
        if abs_path and exists(abs_path) and abs_path != HOME_PATH:
            # 路径在HOME_PAGE内, 且存在, 并且不能删除HOME_PAGE目录
            if isfile(abs_path):
                os.remove(abs_path)  # 删除文件
            else:
                shutil.rmtree(abs_path)

            return create_api_response(CODE_YES)
        else:
            raise Exception('路径错误')
    except Exception as e:
        return create_api_response(CODE_NO, errmsg=str(e))


@bp.route('/mkdir/', methods=['POST'])
@login_required
def api_mkdir():
    """新建文件夹api"""

    # dir: 哪个目录下创建目录 name: 新建的目录名字
    dir = request.form.get('dir') or HOME_PATH
    name = request.form.get('name')  # 若名字为空肯定会创建失败, 不用管)

    abs_dir = get_abs_path(HOME_PATH, join(dir, name))
    try:
        if abs_dir:
            os.mkdir(abs_dir)
            return create_api_response(CODE_YES)
        else:
            raise Exception('不在主路径')
    except Exception as e:
        return create_api_response(CODE_NO, errmsg=str(e))


@bp.route('/upload/', methods=['POST'])
@login_required
def api_upload():
    """上传文件api"""

    # dir: 存放的目录  files: 文件对象的列表
    dir = request.form.get('dir') or HOME_PATH  # 若为空默认为管理的根目录
    files = request.files.getlist('files')

    success_lst = []
    for f in files:
        abs_path = get_abs_path(HOME_PATH, join(dir, f.filename))
        try:
            if abs_path and not exists(abs_path):
                f.save(abs_path)
                success_lst.append(abs_path)
            else:
                raise Exception()
        except Exception as e:
            logging.error(e)

    if success_lst:
        return create_api_response(CODE_YES, data=success_lst)
    else:
        return create_api_response(CODE_NO, errmsg='所有操作失败')


@bp.route('/listdir/', methods=['POST'])
@login_required
def api_listdir():
    """获取目录下内容的api"""

    # dir: 目录名字
    dir = request.form.get('dir') or HOME_PATH  # 传过来的参数为空不影响

    abs_dir = get_abs_path(HOME_PATH, dir)

    try:
        if abs_dir and isdir(abs_dir):
            dirs, files = listdir(abs_dir)
            return create_api_response(CODE_YES, data={'dirs': dirs, 'files': files})
        else:
            raise Exception('找不到目录')
    except Exception as e:
        return create_api_response(CODE_NO, errmsg=str(e))


@bp.route('/copy/', methods=['POST'])
@login_required
def api_copy():
    """复制文件/目录api"""

    # src: 源路径 dst: 目标路径
    src = request.form.get('src')
    dst = request.form.get('dst')

    try:
        if src and dst:  # 保证参数不为空
            abs_src = str(get_abs_path(HOME_PATH, src))  # 源绝对路径(确保在HOME_PATH下)
            abs_dst = str(get_abs_path(HOME_PATH, dst))  # 目标绝对路径(确保在HOME_PATH下)

            if abs_src and abs_dst:
                if isdir(abs_src):
                    # 目录复制用copytree
                    dir_name = basename(abs_src)  # 获取源目录的目录名
                    abs_dst = join(abs_dst, dir_name)  # 拼接实际目标路径(因为前端传来的dst是已经存在的目录)

                    shutil.copytree(abs_src, abs_dst)
                elif isfile(abs_src):
                    # 文件复制用copy
                    shutil.copy(abs_src, abs_dst)
                else:
                    # 不存在abs_src文件或目录
                    raise Exception('%s 找不到' % abs_src)

                return create_api_response(CODE_YES)
            else:
                # 路径不在HOME_PATH里
                raise Exception('路径不在HOME_PATH里')
        else:
            raise Exception('SRC或DST为空')
    except Exception as e:
        return create_api_response(CODE_NO, errmsg=str(e))


@bp.route('/move/', methods=['POST'])
@login_required
def api_move():
    """移动文件api"""

    # src: 源路径 dst: 目标路径
    src = request.form.get('src')
    dst = request.form.get('dst')

    try:
        if src and dst:  # 保证参数不为空
            abs_src = str(get_abs_path(HOME_PATH, src))  # 源绝对路径(确保在HOME_PATH下)
            abs_dst = str(get_abs_path(HOME_PATH, dst))  # 目标绝对路径(确保在HOME_PATH下)

            if abs_src and abs_dst:
                # 无论目录还是文件直接用move即可
                shutil.move(abs_src, abs_dst)
                return create_api_response(CODE_YES)
            else:
                # 路径不在HOME_PATH里
                raise Exception('路径不在HOME_PATH里')
        else:
            raise Exception('SRC或DST为空')
    except Exception as e:
        return create_api_response(CODE_NO, errmsg=str(e))


@bp.route('/rename/', methods=['POST'])
@login_required
def api_rename():
    """重命名文件或目录api"""

    # path: 文件或目录的路径 name: 目录名字
    path = request.form.get('path')
    name = request.form.get('name')
    # 忽略name中有 ../ 等路径分割符, 正常操作不会出现这种状况, 即使出现也只是文件被移动

    try:
        if path and name:
            abs_src = get_abs_path(HOME_PATH, path)  # 源文件名
            abs_dst = get_abs_path(HOME_PATH, join(dirname(abs_src), name))  # 目标文件名

            if abs_src and abs_dst and not exists(abs_dst):
                os.rename(abs_src, abs_dst)
                return create_api_response(CODE_YES)
            else:
                raise Exception(
                    '文件或目录不在主路径或目标路径: %s 已存在.' % abs_dst)
        else:
            raise Exception('路径为空')
    except Exception as e:
        return create_api_response(CODE_NO, errmsg=str(e))


@bp.route('/download/', methods=['GET'])
@login_required
def api_download():
    """下载文件api"""

    # path: 文件的路径
    path = request.args.get('file')

    abs_path = get_abs_path(HOME_PATH, path)

    try:
        if abs_path and exists(abs_path) and isfile(abs_path):
            return send_file(abs_path, as_attachment=True)
        else:
            raise Exception('文件不存在或路径不是文件')
    except Exception as e:
        return create_api_response(CODE_NO, errmsg=str(e))


@bp.route('/view/', methods=['GET'])
@login_required
def api_view():
    """查看文件内容的api"""
    supported_mime_types = [
        'text/plain',
        'text/html',
        'text/css',
        'application/javascript',
        'text/yaml',
        'text/ini',
        'text/x-python',
        'application/json',
        'application/xml',
        'text/csv',
        'text/markdown',
        'application/sql',
        'text/x-shellscript',
        'text/x-php',
        'text/x-ruby',
        'text/x-perl',
        'text/x-java-source',
        'text/x-csrc',
        'text/x-c++src',
        'text/x-csharp',
        'text/x-lua',
        'text/x-rust',
        'text/x-go',
        'text/x-swift',
        # 添加更多你想要支持的MIME类型
    ]
    path = request.args.get('path')

    abs_path = get_abs_path(HOME_PATH, path)

    try:
        if abs_path and exists(abs_path) and isfile(abs_path):
            # 检查文件大小，如果超过100MB，直接返回错误消息
            if os.path.getsize(abs_path) > 100 * 1024 * 1024:
                return create_api_response(CODE_NO, errmsg='文件过大')

            # 使用mimetypes库猜测文件的MIME类型
            mime_type, encoding = mimetypes.guess_type(abs_path)
            if mime_type and mime_type not in supported_mime_types:
                return create_api_response(CODE_NO, errmsg='不支持的文件类型')

            # 尝试使用chardet检测文件编码，只读取文件的前1MB
            with open(abs_path, 'rb') as f:
                result = chardet.detect(f.read(1024 * 1024))

            # 如果检测到的编码的置信度太低，我们认为文件不能被文本编辑器打开
            if result['confidence'] < 0.5:
                return create_api_response(CODE_YES, data={'mime_type': '未知编码', 'editable': False})

            # 使用检测到的编码打开文件
            with open(abs_path, 'r', encoding=result['encoding']) as file:
                content = file.read()
            return create_api_response(CODE_YES, data={'content': content, 'editable': True})
        else:
            raise Exception('文件不存在或路径不是文件')
    except Exception as e:
        return create_api_response(CODE_NO, errmsg=str(e))


@bp.route('/edit/', methods=['POST'])
@login_required
def api_edit():
    """修改文件内容的api"""

    # path: 文件的路径 content: 新的文件内容
    path = request.form.get('path')
    content = request.form.get('content')

    abs_path = get_abs_path(HOME_PATH, path)

    try:
        if abs_path and exists(abs_path) and isfile(abs_path):
            with open(abs_path, 'w') as file:
                file.write(content)
            return create_api_response(CODE_YES)
        else:
            raise Exception(f'路径不存在或不是文件: {abs_path}')
    except Exception as e:
        return create_api_response(CODE_NO, errmsg=str(e))
