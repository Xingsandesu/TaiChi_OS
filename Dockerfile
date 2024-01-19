FROM python:3.10.13-slim-bullseye
LABEL authors="huxin"

# 安装依赖
RUN apt update -y && \
    apt install -y gcc python3-dev ca-certificates

WORKDIR /taichi_os

# 复制应用
COPY . /taichi_os

# 安装依赖
RUN pip install -r requirements.txt

EXPOSE 80
# 入口命令
CMD ["python", "run.py"]