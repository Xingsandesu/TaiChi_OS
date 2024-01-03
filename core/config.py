import os
import sys
import secrets

# 全局基本配置文件



class Config:
    SECRET_KEY = secrets.token_hex(16)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WIN = sys.platform.startswith('win')
    prefix = 'sqlite:///' if WIN else 'sqlite:////'
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(os.path.dirname(__file__), 'data.db')


# @/file 配置文件
HOME_PATH = os.path.abspath('/')  # 将路径转化为标准绝对路径
HOME_NAME = os.path.basename(HOME_PATH)  # 根目录的名字

# @/ 配置文件
index_title = 'Universe OS'
items_dict = {
    'HomeLab': [
        {'title': 'HomeAssistant',
         'link': '/HomeAssistant',
         'logo': 'static/img/ops.png',
         },

        {'title': 'Alist',
         'link': '/Alist',
         'logo': 'static/img/ops.png',
         },

        {'title': 'Emby',
         'link': '/Emby',
         'logo': 'static/img/ops.png',
         },
    ],
    'TEST': [
        {'title': 'TEST1',
         'link': '/HomeAssistant',
         'logo': 'static/img/ops.png',
         },
    ],
}

# @/command 配置文件
commands = {
    'docker ps -a': '显示全部容器',
    'dir': '显示路径',
    'echo hello word': '测试输出',
}
