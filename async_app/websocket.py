import asyncio
import concurrent.futures
import logging
import multiprocessing
import queue
import time
from collections import deque
from datetime import datetime

import psutil
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

from core.config import UNSUPPORTED_COMMANDS, TAICHI_OS_LOGO

################ 系统信息Websocket ################

MAXLEN = 10
UPDATE_INTERVAL = 1  # 更新间隔，单位：秒


class SystemMonitor:
    def __init__(self):
        self.data_table = {
            "local_time": deque([""] * MAXLEN, maxlen=MAXLEN),
            "cpu_load": [deque([0] * MAXLEN, maxlen=MAXLEN) for _ in range(3)],
            "memory_usage": deque([0] * MAXLEN, maxlen=MAXLEN),
            "upload_speed": deque([0] * MAXLEN, maxlen=MAXLEN),
            "download_speed": deque([0] * MAXLEN, maxlen=MAXLEN),
            "disk_read_speed": deque([0] * MAXLEN, maxlen=MAXLEN),
            "disk_write_speed": deque([0] * MAXLEN, maxlen=MAXLEN),
        }

        self.clients = set()  # 用于存储所有打开的 WebSocket 连接
        self.is_loop_running = False  # 用于跟踪数据更新循环是否正在运行

        # 初始化网络 I/O 和磁盘 I/O 统计数据
        self.old_net_io_stats = psutil.net_io_counters()
        self.old_disk_io_stats = psutil.disk_io_counters()
        self.loop_task = None  # 用于存储当前正在运行的数据更新循环任务


class MonitorHandler(tornado.websocket.WebSocketHandler):
    monitor = None  # 类变量，用于存储 SystemMonitor 实例

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        if MonitorHandler.monitor is None:  # 如果还没有 SystemMonitor 实例，就创建一个
            MonitorHandler.monitor = SystemMonitor()
        else:
            self.monitor = MonitorHandler.monitor  # 使用已存在的 SystemMonitor 实例

    def check_origin(self, origin):
        return True

    def open(self):
        self.monitor.clients.add(self)  # 将新的 WebSocket 连接添加到 clients 集合中
        logging.info("WebSocket资源监控连接建立成功..")
        if not self.monitor.loop_task or self.monitor.loop_task.done():  # 如果数据更新循环未运行，则启动它
            self.monitor.loop_task = asyncio.create_task(self.data_update_loop())

    def on_message(self, message):
        logging.info("WebSocket资源监控连接收到消息: %s", message)

    def on_close(self):
        self.monitor.clients.remove(self)  # 从 clients 集合中移除关闭的 WebSocket 连接
        logging.warning("WebSocket资源监控连接建立关闭..")
        if not self.monitor.clients and self.monitor.loop_task:  # 如果没有打开的 WebSocket 连接，则取消数据更新循环
            self.monitor.loop_task.cancel()
            self.monitor.loop_task = None

    async def data_update_loop(self):
        while self.monitor.clients:  # 只有当有打开的 WebSocket 连接时，才运行数据更新循环
            start_time = time.perf_counter()  # 记录开始时间 (精确到小数点后 6 位) 纠正时延

            data = datetime.now().strftime("%H:%M:%S")
            cpu = psutil.cpu_percent(interval=None, percpu=True)
            memory = psutil.virtual_memory().percent
            new_net_io_stats = psutil.net_io_counters()
            upload_speed_value = new_net_io_stats.bytes_sent - self.monitor.old_net_io_stats.bytes_sent
            download_speed_value = new_net_io_stats.bytes_recv - self.monitor.old_net_io_stats.bytes_recv
            self.monitor.old_net_io_stats = new_net_io_stats

            new_disk_io_stats = psutil.disk_io_counters()
            disk_read_speed_value = new_disk_io_stats.read_bytes - self.monitor.old_disk_io_stats.read_bytes
            disk_write_speed_value = new_disk_io_stats.write_bytes - self.monitor.old_disk_io_stats.write_bytes
            self.monitor.old_disk_io_stats = new_disk_io_stats

            self.monitor.data_table["local_time"].append(data)
            for i in range(3):
                self.monitor.data_table["cpu_load"][i].append(int(cpu[i]))
            self.monitor.data_table["memory_usage"].append(int(memory))
            self.monitor.data_table["upload_speed"].append(upload_speed_value)
            self.monitor.data_table["download_speed"].append(download_speed_value)
            self.monitor.data_table["disk_read_speed"].append(disk_read_speed_value)
            self.monitor.data_table["disk_write_speed"].append(disk_write_speed_value)

            for info_client in self.monitor.clients:  # 遍历所有打开的 WebSocket 连接
                try:
                    if info_client.ws_connection:  # 检查 WebSocket 连接是否仍然打开
                        info_client.write_message({
                            "datetime": list(self.monitor.data_table["local_time"]),
                            "cpu": {
                                "load1": list(self.monitor.data_table["cpu_load"][0]),
                                "load5": list(self.monitor.data_table["cpu_load"][1]),
                                "load15": list(self.monitor.data_table["cpu_load"][2])
                            },
                            "ram": {
                                "memory": list(self.monitor.data_table["memory_usage"])
                            },
                            "network": {
                                "upload": list(self.monitor.data_table["upload_speed"]),
                                "download": list(self.monitor.data_table["download_speed"])
                            },
                            "diskIO": {
                                "disk_read": list(self.monitor.data_table["disk_read_speed"]),
                                "disk_write": list(self.monitor.data_table["disk_write_speed"])
                            }
                        })

                    else:
                        raise Exception("WebSocket 连接已经关闭!")
                except tornado.websocket.WebSocketClosedError:
                    logging.error("WebSocket 连接已经关闭!")

            elapsed_time = time.perf_counter() - start_time  # 计算实际执行时间
            sleep_time = max(0.0, UPDATE_INTERVAL - elapsed_time)  # 计算需要睡眠的时间，如果实际执行时间超过了间隔时间，那么就不需要睡眠 纠正时延
            await asyncio.sleep(sleep_time)  # 使用更精确的睡眠函数


################ 系统信息Websocket结束 ################

################ Docker日志和终端 ################
from core.models import client as docker_client


def fetch_logs(container_id, logs_queue, event):
    """从指定的 Docker 容器获取日志，并将其放入队列中"""
    container = docker_client.containers.get(container_id)
    for log in container.logs(stream=True, tail=50):
        logs_queue.put(log.decode('utf-8'))
        event.set()


class DockerLogsHandler(tornado.websocket.WebSocketHandler):
    """处理 Docker 容器日志的 WebSocket 处理器"""

    def open(self, container_id):
        """WebSocket 连接打开时的操作"""
        logging.info(f"{container_id} 容器日志输出Websocket连接建立成功..")
        self.write_message(TAICHI_OS_LOGO)
        self.logs_queue = multiprocessing.Queue()
        self.event = multiprocessing.Event()
        self.process = multiprocessing.Process(target=fetch_logs, args=(container_id, self.logs_queue, self.event))
        self.process.start()
        tornado.ioloop.IOLoop.current().spawn_callback(self.send_logs)

    async def send_logs(self):
        """从队列中获取日志并发送"""
        while True:
            try:
                log = self.logs_queue.get_nowait()
                await self.write_message(log)
                self.event.clear()
            except queue.Empty:
                await asyncio.sleep(1)  # sleep for a while before trying again
                continue

    async def on_message(self, message):
        """处理接收到的消息"""
        pass

    def on_close(self):
        """WebSocket 连接关闭时的操作"""
        self.process.terminate()
        self.process.join()  # 等待子进程结束
        logging.info(f"容器日志输出Websocket连接建立关闭..")

        # 清空队列中的日志
        while not self.logs_queue.empty():
            try:
                self.logs_queue.get_nowait()
            except queue.Empty:
                break


class DockerBashHandler(tornado.websocket.WebSocketHandler):
    def open(self, container_id):
        logging.info(f"{container_id} 容器运行命令Websocket连接建立成功..")
        self.container = docker_client.containers.get(container_id)
        self.write_message(TAICHI_OS_LOGO)
        self.write_message("容器终端连接成功，请不要输入可交互命令")

    def on_message(self, message):
        if any(command in message for command in UNSUPPORTED_COMMANDS):
            error_message = f"不支持的命令: {message}"
            self.write_message(error_message)
            logging.info(error_message)
        else:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self.container.exec_run, cmd=message, stdout=True, stderr=True, stdin=True,
                                         tty=False)
                try:
                    exec_id = future.result(timeout=2)
                    self.write_message(exec_id.output)
                    logging.info(f"容器运行命令:{message}")
                    logging.info(f"回复:{exec_id.output}")
                except concurrent.futures.TimeoutError:
                    self.write_message("命令执行超时，已被强制终止。")
                    logging.info("命令执行超时，已被强制终止。")

    def on_close(self):
        docker_client.close()
        logging.info(f"容器运行命令Websocket连接建立关闭..")
