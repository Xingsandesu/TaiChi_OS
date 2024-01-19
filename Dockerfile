FROM python:3.11.7-alpine
LABEL authors="huxin"

# 安装依赖
RUN apk update && \
    apk add --no-cache ca-certificates && mkdir -p /taichi_os/work

WORKDIR /taichi_os

# 复制应用
COPY . /taichi_os

# 安装依赖
RUN pip install -r requirements.txt

EXPOSE 80
# 入口命令
CMD ["python", "run.py"]