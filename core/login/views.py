from datetime import timedelta

from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from flask_login import login_user, login_required, logout_user

from core.models import User, db

bp = Blueprint('login', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # 检查数据库中是否已经存在用户
    if User.query.first():
        # 如果存在用户，重定向到主页
        flash('已经有账户了，请登录')
        return redirect(url_for('login.login'))
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            if not username or not password:
                flash('输入无效')
                return redirect(url_for('login.register'))

            if User.user_exists(username):
                flash('用户名已存在')
                return redirect(url_for('login.register'))

            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash('注册成功，请登录')
            return redirect(url_for('login.login'))

        return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # 检查数据库中是否已经存在用户
    if not User.query.first():
        # 如果不存在用户，重定向到注册页面
        flash('欢迎首次使用TaiChi OS, 请注册')
        return redirect(url_for('login.register'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('输入无效')
            return redirect(url_for('login.login'))

        user = User.query.filter_by(username=username).first()

        # 验证用户名和密码是否一致
        try:
            if username == user.username and user.validate_password(password):
                login_user(user)  # 登入用户
                session.permanent = True
                bp.permanent_session_lifetime = timedelta(days=1)
                db.session.commit()
                next_page = session.get('next', url_for('index.index'))  # 获取保存在 session 中的原来的 URL
                return redirect(next_page)  # 重定向到原来的 URL
            else:
                flash('用户名或密码无效')  # 如果验证失败，显示错误消息
                return redirect(url_for('login.login'))  # 重定向回登录页面
        except AttributeError:
            flash('用户名或密码无效')  # 如果验证失败，显示错误消息
            return redirect(url_for('login.login'))  # 重定向回登录页面

    session['next'] = request.args.get('next')  # 在用户登录前保存他们原来访问的 URL
    return render_template('login.html')


@bp.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('')
    return redirect(url_for('login.login'))  # 重定向回首页
