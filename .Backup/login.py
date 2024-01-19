from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
import sqlalchemy_utils
import os
import sys
import click
import secrets


app = Flask(__name__, template_folder='index/templates', static_folder='index/static')
app.config['SECRET_KEY'] = secrets.token_hex(16)
# 判断系统类型
WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

# sqlite:///数据库文件的绝对地址,如果你使用 Windows 系统只需要写入三个斜线（即 sqlite:///）
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_type = db.Column(db.String(255))
    username = db.Column(db.String(255))
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值


# 使用 click.option() 装饰器设置的两个选项分别用来接受输入用户名和密码。执行 flask admin 命令，输入用户名和密码后，即可创建管理员账户。
@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    # 判断数据库是否存在
    if sqlalchemy_utils.functions.database_exists(prefix + os.path.join(app.root_path, 'data.db')):
        print('Database already exists.')
    else:
        print('Create database.')
        db.create_all()

    if db.session.query(User.id).filter_by(username=username).scalar() is not None:
        user = User.query.filter_by(username=username).first()
        click.echo('Updating user...')
        user.set_password(password)  # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, user_type='Admin')
        user.set_password(password)  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交数据库会话
    click.echo('Done.')


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('输入无效')
            return redirect(url_for('login'))
        user = User.query.filter_by(username=username).first()
        # 验证用户名和密码是否一致
        try:
            if username == user.username and user.validate_password(password):
                login_user(user)  # 登入用户
                next_page = session.get('next', url_for('index.index'))  # 获取保存在 session 中的原来的 URL
                return redirect(next_page)  # 重定向到原来的 URL
        except AttributeError:
            flash('用户名或密码无效')  # 如果验证失败，显示错误消息
            return redirect(url_for('login'))  # 重定向回登录页面

        flash('用户名或密码无效')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    session['next'] = request.args.get('next')  # 在用户登录前保存他们原来访问的 URL
    return render_template('login.html')


@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('再见')
    return redirect(url_for('login'))  # 重定向回首页