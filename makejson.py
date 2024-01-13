import json

# 定义端口映射
ports = {'3002/tcp': 3002}

# 定义卷映射
volumes = {
    '~/docker_data/sun-panel/conf': {'bind': '/app/conf', 'mode': 'rw'},
    '~/docker_data/sun-panel/uploads': {'bind': '/app/uploads', 'mode': 'rw'},
    '~/docker_data/sun-panel/database': {'bind': '/app/database', 'mode': 'rw'}
}

# 定义容器配置
container_config = {
    'image': 'hslr/sun-panel',
    'name': 'sun-panel',
    'ports': ports,
    'volumes': volumes,
    'restart_policy': {'Name': 'always'}
}

# 格式化为JSON
json_data = json.dumps(container_config, indent=4)

print(json_data)
