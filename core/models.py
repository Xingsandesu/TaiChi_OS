import logging
import os
import urllib.request
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from os.path import join, isdir, abspath, pardir, basename, getmtime
from secrets import token_hex
from sys import exit, stdout, argv
from time import localtime, asctime

import requests
from docker import from_env
from flask import request
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from lxml import html
from werkzeug.security import generate_password_hash, check_password_hash

from core.config import DOCKER_CATEGORY, DEFAULT_LOGO_PATH

db = SQLAlchemy()

try:
    client = from_env()
except Exception as e:
    logging.error(e)
    try:
        import subprocess
        from core.config import INSTLL_DOCKER_COMMANDS, GET_DOCKER_SHELL_COMMAND

        logging.error("未找到DockerSocket,可能是未安装Docker,是否安装Docker?")
        logging.warning("-----安装方式-----")
        logging.warning("1. 官方脚本安装")
        logging.warning("2. 官方二进制分发")
        logging.warning("注意: 不到万不得已不要二进制安装Docker，因为无法使用包管理更新, 只在RHEL 9上测试通过!!!")
        logging.warning("详细请查看: https://docs.docker.com/engine/install/")
        user_input = input("请输入选项( 1, 2 ):").lower()
        if user_input in ['1']:
            process = subprocess.Popen(GET_DOCKER_SHELL_COMMAND, shell=True, stdout=stdout)
            process.wait()
            if process and process.returncode != 0:
                logging.error("Docker安装失败! 请检查网络或者使用root权限")
                exit()
            else:
                logging.info("Docker安装成功!")
                logging.info("程序正在启动...")
                client = DockerClient.from_env()
        elif user_input in ['2']:
            process = subprocess.Popen(INSTLL_DOCKER_COMMANDS, shell=True, stdout=stdout)
            process.wait()
            if process and process.returncode != 0:
                logging.error("Docker安装失败! 请检查网络或者使用root权限")
                exit()
            else:
                logging.info("Docker安装成功!")
                logging.info("程序正在启动...")
                client = DockerClient.from_env()
        else:
            logging.error("无效的输入!")
            exit()
    except KeyboardInterrupt:
        logging.info("用户结束进程")
        exit()


######################### 数据库相关Class #########################
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_type = db.Column(db.String(255))
    username = db.Column(db.String(255))
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值

    @classmethod
    def user_exists(cls, username):
        return cls.query.filter_by(username=username).first() is not None


class Config:
    SECRET_KEY = token_hex(16)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    prefix = 'sqlite:///'
    db_dir = os.path.join(os.path.dirname(argv[0]), 'work')

    # 确保数据库目录存在
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(db_dir, 'data.db')


######################### 数据库相关Class结束 #########################

######################### 主页相关Class #########################
# @/ 配置文件
class Items:
    def __init__(self):
        self.items_dict = {}

    def add_category(self, category_name, category_items):
        self.items_dict[category_name] = category_items

    def delete_category(self, category_name):
        if category_name in self.items_dict:
            del self.items_dict[category_name]

    def update_category(self, category_name, category_items):
        if category_name in self.items_dict:
            self.items_dict[category_name] = category_items

    def get_category(self, category_name):
        return self.items_dict.get(category_name, None)

    def add_item_to_category(self, category_name, item):
        if category_name in self.items_dict:
            self.items_dict[category_name].append(item)

    def delete_item_from_category(self, category_name, item):
        if category_name in self.items_dict and item in self.items_dict[category_name]:
            self.items_dict[category_name].remove(item)

    def item_exists_in_category(self, category_name, item):
        if category_name in self.items_dict:
            return item in self.items_dict[category_name]
        return False

    def remove_nonexistent_items(self, category_name, existing_items):
        if category_name in self.items_dict:
            self.items_dict[category_name] = [item for item in self.items_dict[category_name] if item in existing_items]


### index docker相关
items = Items()


class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: str, default=0):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        else:
            return default

    def put(self, key: str, value: int):
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value


failed_urls = LRUCache(1000)


def get_url_content(url: str, timeout=1.0):
    if failed_urls.get(url) >= 2:
        return None

    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return response.text
    except Exception as error:
        failed_urls.put(url, failed_urls.get(url, 0) + 1)
        logging.error(f"获取URL时出错: {url}: {error}")
        return None


def get_favicon_url(base_url: str):
    """
    获取指定URL的favicon图标的URL。

    参数:
    base_url (str): 要获取favicon的URL。

    返回:
    str: favicon的URL。如果没有找到favicon，返回默认的logo路径。
    """
    max_icon_size = 0
    icon_url = None
    single_icon_without_size = None

    # 获取所有的图标链接和它们的尺寸
    html_content = get_url_content(base_url)
    if html_content:
        tree = html.fromstring(html_content)
        icons = tree.xpath(
            '//link[@rel="icon" or @rel="shortcut icon" or @type="image/png" or @type="image/svg+xml" or @type="image/jpeg"]')

        # 如果只有一个图标，直接返回
        if len(icons) == 1:
            return urllib.parse.urljoin(base_url, icons[0].get('href'))

        # 如果没有找到带尺寸的图标，但找到了一个没有尺寸的图标，返回这个图标
        if icon_url is None:
            icon_url = single_icon_without_size if single_icon_without_size else DEFAULT_LOGO_PATH

        # 遍历图标 找到最大的
        for icon in icons:
            size = icon.get('sizes')
            if size:
                try:
                    # 尺寸可能是像 "16x16" 这样的格式，我们只需要其中的一个数字
                    icon_size = int(size.split('x')[0])
                    if icon_size > max_icon_size:
                        max_icon_size = icon_size
                        icon_url = urllib.parse.urljoin(base_url, icon.get('href'))
                except ValueError as error:
                    logging.warning(f"应用容器图标错误: {error}")
            elif single_icon_without_size is None:
                single_icon_without_size = urllib.parse.urljoin(base_url, icon.get('href'))

    else:
        icon_url = DEFAULT_LOGO_PATH
    return icon_url


def get_docker_info(container: str, server_ip: str):
    """
    获取Docker容器的信息。

    参数:
    container (str): Docker容器。
    server_ip (str): 服务器IP。

    返回:
    dict: 包含容器的标题、链接和logo的字典，如果没有映射端口则返回None。
    """
    app_name = container.name
    ports = container.ports
    mapped_ports = [port_info[0]['HostPort'] for port_info in ports.values() if port_info]
    if not mapped_ports:  # 选择host网络和macvlan网络的容器返回None
        return None

    base_link = f'http://{server_ip}'
    link = f'{base_link}:{mapped_ports[0]}' if mapped_ports else base_link

    with ThreadPoolExecutor(max_workers=10) as executor:
        logo_path = executor.submit(get_favicon_url, link).result()

    return {'title': app_name, 'link': link, 'logo': logo_path}


def update_docker():
    """
    更新Docker容器的信息。

    该函数会获取所有Docker容器的信息，并将新的容器添加到items中，同时删除不再存在的容器。
    """
    dockers = client.containers.list()
    server_ip = request.host.split(':')[0]

    with ThreadPoolExecutor(max_workers=10) as executor:
        existing_items = list(filter(None, executor.map(lambda container: get_docker_info(container, server_ip),
                                                        dockers)))  # 过滤掉host网络和macvlan网络的容器(None)

    if DOCKER_CATEGORY not in items.items_dict:
        items.add_category(DOCKER_CATEGORY, existing_items)
    else:
        for item in existing_items:
            if not items.item_exists_in_category(DOCKER_CATEGORY, item):
                items.add_item_to_category(DOCKER_CATEGORY, item)
        items.remove_nonexistent_items(DOCKER_CATEGORY, existing_items)


######################### 主页相关Class结束 #########################


######################### files相关def #########################
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
        lst.append((path, asctime(localtime(m_time))))

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

######################### files相关def结束 #########################

######################### 废弃代码 #########################
#
# class Category(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键，自动递增
#     title = db.Column(db.String(255), unique=True)  # 类别字段
#
#     @classmethod
#     def add_category(cls, title):
#         # 创建一个新的Category实例并添加到数据库
#         category = cls(title=title)
#         db.session.add(category)
#         db.session.commit()
#
#     @classmethod
#     def delete_category(cls, title):
#         # 从数据库中删除一个Category实例以及其下的所有Item实例
#         category = cls.query.filter_by(title=title).first()
#         if category:
#             Item.query.filter_by(category_id=category.id).delete()
#             db.session.delete(category)
#             db.session.commit()
#
#     @classmethod
#     def get_all(cls):
#         # 从数据库中获取所有的Category实例
#         categories = cls.query.all()
#         result = {}
#         for category in categories:
#             items = Item.get_all(category.id)
#             result[category.title] = items
#         return result
#
# class Item(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键，自动递增
#     title = db.Column(db.String(255), unique=True)  # 标题字段，设置为唯一
#     link = db.Column(db.String(255))  # 链接字段
#     logo = db.Column(db.String(255))  # logo字段
#     category_id = db.Column(db.Integer, db.ForeignKey('category.id'))  # 外键，关联Category模型
#
#     @classmethod
#     def add_item(cls, category_title, title, link, logo):
#         # 创建一个新的Item实例并添加到数据库
#         category = Category.query.filter_by(title=category_title).first()
#         if category:
#             item = cls(title=title, link=link, logo=logo, category_id=category.id)
#             db.session.add(item)
#             db.session.commit()
#
#     @classmethod
#     def delete_item(cls, title):
#         # 从数据库中删除一个Item实例
#         item = cls.query.filter_by(title=title).first()
#         if item:
#             db.session.delete(item)
#             db.session.commit()
#
#     @classmethod
#     def update_item(cls, title, new_title, link, logo):
#         # 更新数据库中的一个Item实例
#         item = cls.query.filter_by(title=title).first()
#         if item:
#             item.title = new_title
#             item.link = link
#             item.logo = logo
#             db.session.commit()
#
#     @classmethod
#     def get_item(cls, title):
#         # 从数据库中获取一个Item实例
#         return cls.query.filter_by(title=title).first()
#
#     @classmethod
#     def get_all(cls, category_id):
#         # 从数据库中获取所有的Item实例
#         items = cls.query.filter_by(category_id=category_id).all()
#         return [{'title': item.title, 'link': item.link, 'logo': item.logo} for item in items]
#
# '''
# from models import Category, Item
#
# # 获取所有的数据
# data = Category.get_all()
#
# # 添加一个新的类别
# Category.add_category('新类别')
#
# # 删除一个类别
# Category.delete_category('新类别')
#
# # 获取所有类别及其下的所有项目
# categories = Category.get_all()
# for category_title, items in categories.items():
#     print(f'类别: {category_title}')
#     for item in items:
#         print(f'项目: {item["title"]}, 链接: {item["link"]}, logo: {item["logo"]}')
#
# # 添加一个新的项目
# Item.add_item('新类别', '新项目', 'http://example.com', 'http://example.com/logo.png')
#
# # 删除一个项目
# Item.delete_item('新项目')
#
# # 更新一个项目
# Item.update_item('新项目', '新项目2', 'http://example2.com', 'http://example2.com/logo.png')
#
# # 获取一个项目
# item = Item.get_item('新项目2')
# if item:
#     print(f'项目: {item.title}, 链接: {item.link}, logo: {item.logo}')
#
# # 获取一个类别下的所有项目
# items = Item.get_all(1)  # 假设类别ID为1
# for item in items:
#     print(f'项目: {item["title"]}, 链接: {item["link"]}, logo: {item["logo"]}')
# '''
######################### 废弃代码结束 #########################
