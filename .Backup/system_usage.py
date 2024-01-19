import logging
from collections import deque
from datetime import datetime, timedelta

import psutil
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

MAXLEN = 10
UPDATE_INTERVAL = 1  # 更新间隔，单位：秒

data_table = {
    "local_time": deque([""] * MAXLEN, maxlen=MAXLEN),
    "cpu_load": [deque([0] * MAXLEN, maxlen=MAXLEN) for _ in range(3)],
    "memory_usage": deque([0] * MAXLEN, maxlen=MAXLEN),
    "upload_speed": deque([0] * MAXLEN, maxlen=MAXLEN),
    "download_speed": deque([0] * MAXLEN, maxlen=MAXLEN),
    "disk_read_speed": deque([0] * MAXLEN, maxlen=MAXLEN),
    "disk_write_speed": deque([0] * MAXLEN, maxlen=MAXLEN),
}

clients = set()  # 用于存储所有打开的 WebSocket 连接

# 初始化网络 I/O 和磁盘 I/O 统计数据
old_net_io_stats = psutil.net_io_counters()
old_disk_io_stats = psutil.disk_io_counters()


class MonitorHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        clients.add(self)  # 将新的 WebSocket 连接添加到 clients 集合中
        logging.info("WebSocket资源监控连接建立成功..")

    def on_message(self, message):
        pass

    def on_close(self):
        clients.remove(self)  # 从 clients 集合中移除关闭的 WebSocket 连接
        logging.warning("WebSocket资源监控连接建立关闭..")


def data_update_loop():
    global old_net_io_stats, old_disk_io_stats
    print("循环")
    data = datetime.now().strftime("%H:%M:%S")
    cpu = psutil.cpu_percent(interval=None, percpu=True)
    memory = psutil.virtual_memory().percent
    new_net_io_stats = psutil.net_io_counters()
    upload_speed_value = new_net_io_stats.bytes_sent - old_net_io_stats.bytes_sent
    download_speed_value = new_net_io_stats.bytes_recv - old_net_io_stats.bytes_recv
    old_net_io_stats = new_net_io_stats

    new_disk_io_stats = psutil.disk_io_counters()
    disk_read_speed_value = new_disk_io_stats.read_bytes - old_disk_io_stats.read_bytes
    disk_write_speed_value = new_disk_io_stats.write_bytes - old_disk_io_stats.write_bytes
    old_disk_io_stats = new_disk_io_stats

    data_table["local_time"].append(data)
    for i in range(3):
        data_table["cpu_load"][i].append(int(cpu[i]))
    data_table["memory_usage"].append(int(memory))
    data_table["upload_speed"].append(upload_speed_value)
    data_table["download_speed"].append(download_speed_value)
    data_table["disk_read_speed"].append(disk_read_speed_value)
    data_table["disk_write_speed"].append(disk_write_speed_value)

    for client in clients:  # 遍历所有打开的 WebSocket 连接
        try:
            if client.ws_connection:  # 检查 WebSocket 连接是否仍然打开
                client.write_message({
                    "datetime": list(data_table["local_time"]),
                    "cpu": {
                        "load1": list(data_table["cpu_load"][0]),
                        "load5": list(data_table["cpu_load"][1]),
                        "load15": list(data_table["cpu_load"][2])
                    },
                    "ram": {
                        "memory": list(data_table["memory_usage"])
                    },
                    "network": {
                        "upload": list(data_table["upload_speed"]),
                        "download": list(data_table["download_speed"])
                    },
                    "diskIO": {
                        "disk_read": list(data_table["disk_read_speed"]),
                        "disk_write": list(data_table["disk_write_speed"])
                    }
                })

            else:
                raise Exception("WebSocket 连接已经关闭!")
        except tornado.websocket.WebSocketClosedError:
            logging.error("WebSocket 连接已经关闭!")
    tornado.ioloop.IOLoop.current().add_timeout(timedelta(seconds=1), data_update_loop)


def monitor_app():
    return [
        (r'/Monitor', MonitorHandler),
    ]


# 启动服务器
if __name__ == "__main__":
    tornado.httpserver.HTTPServer(monitor_app()).listen(8888)
    tornado.ioloop.IOLoop.current().start()
