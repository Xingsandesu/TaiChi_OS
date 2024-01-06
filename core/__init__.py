from flask import Flask
from flask_login import LoginManager

from core.models import db, User, Config
from .api import *
from .index import bp as index_bp
from .login.views import bp as login_bp

app = Flask(__name__, template_folder='html/templates', static_folder='html/static')
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login.login'
login_manager.login_message = ''


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象


def create_app():
    with app.app_context():
        db.create_all()
    app.register_blueprint(api.bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(login_bp)

    return app
