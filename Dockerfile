FROM python:3.11.7-slim-bookworm
LABEL authors="huxin"

# 安装依赖
RUN apt-get update && \
    apt-get install -y gcc python3-dev ca-certificates && mkdir -p /taichi_os/work

WORKDIR /taichi_os

# 复制应用
COPY . /taichi_os

# 安装依赖
RUN pip install -r requirements.txt

EXPOSE 80
# 入口命令
CMD ["python", "run.py"]