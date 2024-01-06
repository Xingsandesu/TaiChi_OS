import os

# 全局基本配置文件

# @/file 配置文件
HOME_PATH = os.path.abspath('/')  # 将路径转化为标准绝对路径
HOME_NAME = os.path.basename(HOME_PATH)  # 根目录的名字

DEFAULT_LOGO_PATH = 'static/img/ops.png'
DOCKER_CATEGORY = 'Docker Apps'

APP_LOGO_MAPPING = {
    'app1': 'static/img/ops.png',
    'app2': 'static/img/ops.png',
}
# # @/command 配置文件
# commands = {
#     'docker ps -a': '显示全部容器',
#     'dir': '显示路径',
#     'echo hello word': '测试输出',
# }
