from async_app.websocket import MonitorHandler, DockerBashHandler,DockerLogsHandler
from async_app.http import CreateContainerHandler
def async_app():
    return ([
        (r'/Monitor', MonitorHandler),
        (r"/containers/(.*)/logs", DockerLogsHandler),
        (r"/containers/(.*)/bash", DockerBashHandler),
        (r"/api/containers/(.*)/create", CreateContainerHandler)
    ])