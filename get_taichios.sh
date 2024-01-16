#!/bin/bash

# 覆盖/etc/docker/daemon.json
cat << EOF > /etc/docker/daemon.json
{
     "registry-mirrors": [
             "https://mirror.ccs.tencentyun.com"
    ]
}
EOF
echo "Docker镜像加速配置完成"

# 创建目录
mkdir -p /usr/taichi
echo "目录创建完成"

# 下载文件到创建的目录
wget -P /usr/taichi https://example.com/path/to/file
echo "文件下载完成"

# 写入service
cat << EOF > /etc/systemd/system/taichi.service
[Unit]
Description=Taichi
Documentation=https://app.kookoo.top
After=network.target
Wants=network.target

[Service]
WorkingDirectory=/usr/taichi
ExecStart=/usr/taichi/TAICHI_OS
Restart=on-abnormal
RestartSec=5s
KillMode=mixed

StandardOutput=null
StandardError=syslog

[Install]
WantedBy=multi-user.target
EOF
echo "服务写入完成"

# 更新配置
systemctl daemon-reload
echo "配置更新完成"

# 启动服务
systemctl start taichi
echo "服务启动完成"

# 设置开机启动
systemctl enable taichi
echo "设置开机启动完成"