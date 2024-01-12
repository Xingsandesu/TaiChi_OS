import os

# 全局基本配置文件

# @/file 配置文件
HOME_PATH = os.path.abspath('/')  # 将路径转化为标准绝对路径
HOME_NAME = os.path.basename(HOME_PATH)  # 根目录的名字

DEFAULT_LOGO_PATH = 'static/img/ops.png'
DOCKER_CATEGORY = 'Docker Apps'


DOCKER_DOWNLOAD_URL = 'https://download.docker.com/linux/static/stable/x86_64/docker-24.0.7.tgz'

DOCKER_SERVICE_CONFIG = (
    "[Unit]\n"
    "Description=Docker Application Container Engine\n"
    "Documentation=https://docs.docker.com\n"
    "After=network-online.target firewalld.service\n"
    "Wants=network-online.target\n"
    "[Service]\n"
    "Type=notify\n"
    "ExecStart=/usr/bin/dockerd\n"
    "ExecReload=/bin/kill -s HUP $MAINPID\n"
    "LimitNOFILE=infinity\n"
    "LimitNPROC=infinity\n"
    "LimitCORE=infinity\n"
    "TimeoutStartSec=0\n"
    "Delegate=yes\n"
    "KillMode=process\n"
    "Restart=on-failure\n"
    "StartLimitBurst=3\n"
    "StartLimitInterval=60s\n"
    "[Install]\n"
    "WantedBy=multi-user.target\n"
)

INSTLL_DOCKER_COMMANDS = [
    f'rm -rf /usr/bin/docker* && \
    rm -rf /usr/bin/runc && \
    rm -rf /usr/bin/ctr && \
    rm -rf /usr/bin/containerd* && \
    rm -rf /etc/systemd/system/docker* && \
    rm -rf /var/lib/docker* && \
    rm -rf /var/run/docker.sock && \
    curl -o docker.tgz {DOCKER_DOWNLOAD_URL} && \
    tar xzvf docker.tgz && \
    cp docker/* /usr/bin/ && \
    rm -rf docker && \
    echo "{DOCKER_SERVICE_CONFIG}" > /etc/systemd/system/docker.service && \
    chmod +x /etc/systemd/system/docker.service && \
    systemctl daemon-reload && \
    systemctl enable --now docker.service'
]

GET_DOCKER_SHELL_COMMAND = [
    'curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh'
]
# # @/command 配置文件
# commands = {
#     'docker ps -a': '显示全部容器',
#     'dir': '显示路径',
#     'echo hello word': '测试输出',
# }

# def get_latest_docker_url(base_url: str):
#     # 打开URL并读取内容
#     with urllib.request.urlopen(base_url) as response:
#         html = response.read().decode()
#
#     # 使用正则表达式匹配所有的docker版本链接
#     matches = re.findall(r'docker-(\d+\.\d+\.\d+)\.tgz', html)
#
#     # 对匹配到的版本进行排序，选择最大的版本
#     latest_version = sorted(matches, key=lambda version: list(map(int, version.split('.'))), reverse=True)[0]
#
#     # 拼接完整的URL
#     latest_docker_url = base_url + 'docker-' + latest_version + '.tgz'
#
#     return latest_docker_url
