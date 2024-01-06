from .views import bp

if __name__ == '__main__':
    def create_app():
        from flask import Flask
        # noinspection PyShadowingNames
        app = Flask(__name__, template_folder='templates', static_folder='static')

        app.register_blueprint(bp)
        return app


    app = create_app()
    app.run()
