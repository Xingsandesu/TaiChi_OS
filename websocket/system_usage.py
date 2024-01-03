import asyncio
import logging
import time
from collections import deque
from datetime import datetime

import psutil
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

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

            for client in self.monitor.clients:  # 遍历所有打开的 WebSocket 连接
                try:
                    if client.ws_connection:  # 检查 WebSocket 连接是否仍然打开
                        client.write_message({
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


def monitor_app():
    return [
        (r'/Monitor', MonitorHandler),
    ]


# 启动服务器
if __name__ == "__main__":
    tornado.httpserver.HTTPServer(monitor_app()).listen(8888)
    tornado.ioloop.IOLoop.current().start()
