import os
import secrets
import sys


# 全局基本配置文件
class Config:
    SECRET_KEY = secrets.token_hex(16)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WIN = sys.platform.startswith('win')
    prefix = 'sqlite:///' if WIN else 'sqlite:////'
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


items = Items()

# @/file 配置文件
HOME_PATH = os.path.abspath('/')  # 将路径转化为标准绝对路径
HOME_NAME = os.path.basename(HOME_PATH)  # 根目录的名字

DEFAULT_LOGO_PATH = 'static/img/ops.png'
DOCKER_CATEGORY = 'Docker Apps'

app_logo_mapping = {
    'app1': 'static/img/ops.png',
    'app2': 'static/img/ops.png',
}
# # @/command 配置文件
# commands = {
#     'docker ps -a': '显示全部容器',
#     'dir': '显示路径',
#     'echo hello word': '测试输出',
# }
