import logging
import os
import secrets
import sys
import time
from os.path import join, isdir, abspath, pardir, basename, getmtime

from docker import DockerClient
from flask import request
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from core.config import DOCKER_CATEGORY, DEFAULT_LOGO_PATH, APP_LOGO_MAPPING

db = SQLAlchemy()

try:
    client = DockerClient.from_env()
except BaseException:
    try:
        import subprocess
        from core.config import INSTLL_DOCKER_COMMANDS, GET_DOCKER_SHELL_COMMAND

        logging.error("未找到Docker环境,是否安装Docker?")
        logging.warning("-----安装方式-----")
        logging.warning("1. 官方脚本安装")
        logging.warning("2. 官方二进制分发")
        logging.warning("注意: 不到万不得已不要二进制安装Docker，因为无法使用包管理更新, 只在RHEL 9上测试通过!!!")
        logging.warning("详细请查看: https://docs.docker.com/engine/install/")
        user_input = input("请输入选项( 1, 2 ):").lower()
        if user_input in ['1']:
            process = subprocess.Popen(GET_DOCKER_SHELL_COMMAND, shell=True, stdout=sys.stdout)
            process.wait()
            if process and process.returncode != 0:
                logging.error("Docker安装失败! 请检查网络或者使用root权限")
                sys.exit()
            else:
                logging.info("Docker安装成功!")
                logging.info("程序正在启动...")
                client = DockerClient.from_env()
        elif user_input in ['2']:
            process = subprocess.Popen(INSTLL_DOCKER_COMMANDS, shell=True, stdout=sys.stdout)
            process.wait()
            if process and process.returncode != 0:
                logging.error("Docker安装失败! 请检查网络或者使用root权限")
                sys.exit()
            else:
                logging.info("Docker安装成功!")
                logging.info("程序正在启动...")
                client = DockerClient.from_env()
        else:
            logging.error("无效的输入!")
            sys.exit()
    except KeyboardInterrupt:
        logging.info("用户结束进程")
        sys.exit()


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


### 配置相关Class
class Config:
    SECRET_KEY = secrets.token_hex(16)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    prefix = 'sqlite:///'
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(os.path.dirname(sys.argv[0]), 'data.db')


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


### files相关def
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


### index docker相关def
items = Items()


# 定义一个函数，根据应用名称获取对应的logo路径
def get_logo_path(app_name):
    # 从app_logo_mapping字典中获取应用名称对应的logo路径，如果没有找到，则返回默认的logo路径
    return APP_LOGO_MAPPING.get(app_name, DEFAULT_LOGO_PATH)


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
'''
from models import Category, Item

# 获取所有的数据
data = Category.get_all()

# 添加一个新的类别
Category.add_category('新类别')

# 删除一个类别
Category.delete_category('新类别')

# 获取所有类别及其下的所有项目
categories = Category.get_all()
for category_title, items in categories.items():
    print(f'类别: {category_title}')
    for item in items:
        print(f'项目: {item["title"]}, 链接: {item["link"]}, logo: {item["logo"]}')

# 添加一个新的项目
Item.add_item('新类别', '新项目', 'http://example.com', 'http://example.com/logo.png')

# 删除一个项目
Item.delete_item('新项目')

# 更新一个项目
Item.update_item('新项目', '新项目2', 'http://example2.com', 'http://example2.com/logo.png')

# 获取一个项目
item = Item.get_item('新项目2')
if item:
    print(f'项目: {item.title}, 链接: {item.link}, logo: {item.logo}')

# 获取一个类别下的所有项目
items = Item.get_all(1)  # 假设类别ID为1
for item in items:
    print(f'项目: {item["title"]}, 链接: {item["link"]}, logo: {item["logo"]}')
'''
