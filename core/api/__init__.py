from .blueprint import bp
# from .command import *
from .files import *
from .system_info import *
from .docker import *

if __name__ == '__main__':
    def create_app():
        from flask import Flask
        # noinspection PyShadowingNames
        app = Flask(__name__)
        app.register_blueprint(bp)
        return app


    app = create_app()
    app.run()
