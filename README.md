# 太极OS

---
<div align=center>

<img src="https://github.com/Xingsandesu/TaiChi_OS/blob/master/.logo/logo_transparent.png" width="100" height="100" />


<a href="https://github.com/Xingsandesu/TaiChi_OS">Github</a> | <a href="https://hub.docker.com/repository/docker/fushin/taichios">Docker Hub</a><br>
新一代一体式家庭Docker管理工具

</div>

## 简介

太极OS 是一个新一代面向家庭的Docker管理工具，面向0技术的人群也能轻松上手，目前实现的模块有Web管理模块，太极软件源模块，将来要实现的模块有Cil模块，多节点控制模块，多节点Master模块。

特点：简单 轻松易上手 自带软件商店 免修改代码 使用太极私有软件源可以将任意繁杂的Docker创建流程简化为一个run.json 轻松部署

## 功能列表

| 功能           | 描述                               |
|--------------|----------------------------------|
| 主页导航         | 自动获取正在运行的容器项目添加到主页               |
| Containers管理 | Containers的日志，终端，运行状态监控，开启，关闭等功能 |
| Docker存储卷管理  | Docker存储卷相关功能                    |
| Docker镜像管理   | Docker镜像相关功能                     |
| WebSSH       | 自带一个简单的WebSSH管理工具                |
| 文件管理         | 自带一个简单的文件管理工具                    |
| 监控面板         | 实时监控系统运行状态，CPU，RAM，IO，NETWORK    |
| 应用商店         | 自动从官方软件源下载各种软件，当然也可以自己手动部署一个私有源  |


## 快速开始

### 一键安装

#### AMD64
- 内测二进制支持版本Ubuntu20.04日期往后的所有发行版, Docker支持所有运行Docker的发行版, 源码安装支持主流Linux发行版
```Shell
curl -sSL -o get-taichi.sh https://download.kookoo.top/get-taichi.sh && bash get-taichi.sh
```
- 或者
```Shell
curl -sSL -o get-taichi.sh https://raw.githubusercontent.com/Xingsandesu/TaiChi_OS/master/.shell/get-taichi.sh && bash get-taichi.sh
```
#### ARM64
- 内测二进制支持版本Ubuntu18.04日期往后的所有发行版, Docker支持所有运行Docker的发行版, 源码安装支持主流Linux发行版
- (推荐使用源码或者Docker安装安装, 0.9.7之前升级新版本请先卸载一遍再安装)
```Shell
curl -sSL -o get-taichi.sh https://download.kookoo.top/get-taichi.sh && bash get-taichi.sh
```
- (以下是二进制安装, 随缘更新编译版本)
```Shell
curl -sSL -o get-taichi-arm64.sh https://download.kookoo.top/get-taichi-arm64.sh && bash get-taichi-arm64.sh
```
- 或者
```Shell
curl -sSL -o get-taichi-arm64.sh https://raw.githubusercontent.com/Xingsandesu/TaiChi_OS/master/.shell/get-taichi-arm64.sh && bash get-taichi-arm64.sh
```

### 手动部署 (源码运行)

#### 适用于所有架构？

- 下载源码到本地并且解压
- 进入.shell目录, 修改build.sh, 手动编译安装Python3.11.7, 或者使用包管理工具安装, Python3.10版本以上的版本都可以正常运行
- 返回主目录, python -m pip install -r requirements.txt
- 然后执行 python run.py

### 手动部署(二进制)

#### AMD64 
下载二进制运行
[Github Actions](https://github.com/Xingsandesu/TaiChi_OS/actions)

### 手动编译
见[build.sh](https://github.com/Xingsandesu/TaiChi_OS/blob/master/.shell/build.sh)

## 扩展: 软件源私有部署

[太极OS软件源仓库](https://github.com/Xingsandesu/Taichi_OS_Software_Source)

### 官方源

https://app.kookoo.top

### 手动部署

1. 创建目录

    ```bash
    mkdir /root/taichisource
    mkdir /root/taichisource/app
    touch /root/taichisource/app.json
    ```

2. 运行镜像

    ```bash
    docker run -itd \
    --name software_source \
    -p 10010:10010 \
    -v /root/taichisource/app:/app/app \
    -v /root/taichisource/app.json:/app/app.json \
    --restart=always \
    fushin/taichi_os_software_source
    ```

### TaiChi OS 手动API部署

[POST] http://{host}:{ip}/api/containers/software_source/create

### TaiChi OS 软件商店部署

左上角-软件商店-software_source-安装

### 太极OS内应用软件源

使用安装脚本，选择修改软件源，输入你的软件源地址或者IP，即可完成私有软件源的搭建

### 私有软件源使用教程

搭建完成后，进入软件源页面，准备好你要使用的docker run命令，输入在文本框中，点击生成，即可生成对应版本的run.json，确认无误后，点击确认按钮，即可添加完毕。现在，你添加的应用就可以在太极OS软件商店中获取到了

注意: 目前版本只支持Bridge网络，Host和Macvlan网络等待后续更新

### run.json介绍

#### 什么是run.json?

`run.json`是太极OS运行容器所需要的配置文件，类似于`docker-compose`，但是官方docker sdk并不支持`docker-compose`，而且太极OS本身也并不需要那么多功能，所以使用了`run.json`作为容器运行配置的载体，通过直接解析，响应更快。使用`docker run`命令直接可以转换成`run.json`，学习成本更低

#### 他是怎么工作的?

首先解析了`docker run`命令的关键词，根据关键词匹配参数，使用统一存储卷代替原来的宿主机映射路径，更方便管理。然后根据JSON格式输出对应的`run.json`，实现原理可参照 [太极软件源仓库](https://github.com/Xingsandesu/Taichi_OS_Software_Source)

#### 示例docker run 命令

```bash
docker run -itd \
--name software_source \
-p 10010:10010 \
-v /root/taichisource/app:/app/app \
-v /root/taichisource/app.json:/app/app.json \
-run_cmd "{shell}" \
--restart=always \
fushin/taichi_os_software_source
```

#### 生成的run.json

```json
{
    "image": "fushin/taichi_os_software_source",
    "name": "software_source",
    "ports": {
        "10010": 10010
    },
    "restart_policy": {
        "Name": "always"
    },
    "run_cmd": {
        "software_source_app_volume": [
            "{shell}"
        ]
    },
    "volumes": {
        "software_source_app.json_volume": {
            "bind": "/app/app.json",
            "mode": "rw"
        },
        "software_source_app_volume": {
            "bind": "/app/app",
            "mode": "rw"
        }
    }
}
```

#### 目前支持自定义的:

- images: 镜像名称
- name: 容器名称
- ports: 容器端口:宿主机端口
- restart_policy: 默认为always
- run_cmd: 实验性功能，用于初始化应用需要的某些文件或者执行某些操作，默认绑定最初的存储卷，需要手动指定生成后的存储卷，对于依赖某些网络配置的容器会很好用，可以使用各种shell命令来获取配置。前提是太极OS宿主机内安装了这些shell工具，否则会报错
- env: 环境变量

#### 注意事项

请使用类似如上的`docker run`命令来生成JSON，镜像后面不要带`/bin/bash`，确保镜像是最后一个。生成完毕检查生成的JSON是否与你的命令是否对应，如果不对应可以修改。确认无误后，点击确认，自动写入相对应的`app.json`和`run.json`。注意不要使用过长的名称，不要使用中文名称

## 常见问题及解决方案

1. 如何修改软件源？
- 使用脚本更换软件源

2. 如何恢复默认软件源？
- 使用脚本恢复默认配置

3. 遇到缺失glibc库
- 使用Ubuntu20.04及以上版本的Linux发行版，例如Debian12
- 或者使用Docker部署

4. 我的持久化存储在哪里?
- 太极OS使用存储卷管理容器持久化的内容，存储路径默认在
/var/lib/docker/volumes/卷名/_data,目录结构1:1映射。
5. 遇到报错等问题
- 截图报错日志和遇到问题过程，提交[Issues](https://github.com/Xingsandesu/TaiChi_OS/issues)

## 效果展示
![主页截图](https://github.com/Xingsandesu/TaiChi_OS/blob/master/ScreenShots/web.jpg)
![运行截图](https://github.com/Xingsandesu/TaiChi_OS/blob/master/ScreenShots/cmd.png)

## 兼容性测试-截至2024/1/17

#### 二进制部署运行良好
- Arm64 骁龙410 WIFI棒
- Arm64 RK3566 PurplePi 开发板 系统内核定制支持Docker版本
- Arm64 阿里云Arm ECS实例
- AMD64 R9-5900HS WSL2 Debian12
- AMD64 R9-5900HS Hyper-V Debian12


#### 二进制部署未测试
- AMD64 OpenWRT iStoreOS22.03.52023122916

#### 二进制部署可能存在兼容性问题
- AMD64 腾讯云轻量应用服务器 Debian12 : 容器镜像不显示 : 可能冲突的软件 1Panel

#### Docker部署运行良好
- AMD64 OpenWRT iStoreOS22.03.52023122916
- AMD64 E3v3 PVE 黑群晖DSM7.1.1

## 开源协议
本软件采用GPLv3协议

[![Star History Chart](https://api.star-history.com/svg?repos=Xingsandesu/TaiChi_OS&type=Date)](https://star-history.com/#hslr-s/sun-panel&Date)