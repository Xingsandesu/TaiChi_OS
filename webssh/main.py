import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi

from settings import (
    get_app_settings, get_host_keys_settings, get_policy_setting
)
from webssh.handler import IndexHandler, WsockHandler, NotFoundHandler


def make_app(loop, options):
    host_keys_settings = get_host_keys_settings(options)
    policy = get_policy_setting(options, host_keys_settings)

    handlers = [
        (r'/webssh/', IndexHandler, dict(loop=loop, policy=policy,
                                         host_keys_settings=host_keys_settings)),
        (r'/webssh/ws', WsockHandler, dict(loop=loop))
    ]

    settings = get_app_settings(options)
    settings.update(default_handler_class=NotFoundHandler)

    return tornado.web.Application(handlers, **settings)
