from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_type = db.Column(db.String(255))
    username = db.Column(db.String(255))
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值

    @classmethod
    def user_exists(cls, username):
        return cls.query.filter_by(username=username).first() is not None


#
# class Category(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键，自动递增
#     title = db.Column(db.String(255), unique=True)  # 类别字段
#
#     @classmethod
#     def add_category(cls, title):
#         # 创建一个新的Category实例并添加到数据库
#         category = cls(title=title)
#         db.session.add(category)
#         db.session.commit()
#
#     @classmethod
#     def delete_category(cls, title):
#         # 从数据库中删除一个Category实例以及其下的所有Item实例
#         category = cls.query.filter_by(title=title).first()
#         if category:
#             Item.query.filter_by(category_id=category.id).delete()
#             db.session.delete(category)
#             db.session.commit()
#
#     @classmethod
#     def get_all(cls):
#         # 从数据库中获取所有的Category实例
#         categories = cls.query.all()
#         result = {}
#         for category in categories:
#             items = Item.get_all(category.id)
#             result[category.title] = items
#         return result
#
# class Item(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键，自动递增
#     title = db.Column(db.String(255), unique=True)  # 标题字段，设置为唯一
#     link = db.Column(db.String(255))  # 链接字段
#     logo = db.Column(db.String(255))  # logo字段
#     category_id = db.Column(db.Integer, db.ForeignKey('category.id'))  # 外键，关联Category模型
#
#     @classmethod
#     def add_item(cls, category_title, title, link, logo):
#         # 创建一个新的Item实例并添加到数据库
#         category = Category.query.filter_by(title=category_title).first()
#         if category:
#             item = cls(title=title, link=link, logo=logo, category_id=category.id)
#             db.session.add(item)
#             db.session.commit()
#
#     @classmethod
#     def delete_item(cls, title):
#         # 从数据库中删除一个Item实例
#         item = cls.query.filter_by(title=title).first()
#         if item:
#             db.session.delete(item)
#             db.session.commit()
#
#     @classmethod
#     def update_item(cls, title, new_title, link, logo):
#         # 更新数据库中的一个Item实例
#         item = cls.query.filter_by(title=title).first()
#         if item:
#             item.title = new_title
#             item.link = link
#             item.logo = logo
#             db.session.commit()
#
#     @classmethod
#     def get_item(cls, title):
#         # 从数据库中获取一个Item实例
#         return cls.query.filter_by(title=title).first()
#
#     @classmethod
#     def get_all(cls, category_id):
#         # 从数据库中获取所有的Item实例
#         items = cls.query.filter_by(category_id=category_id).all()
#         return [{'title': item.title, 'link': item.link, 'logo': item.logo} for item in items]
#
'''
from models import Category, Item

# 获取所有的数据
data = Category.get_all()

# 添加一个新的类别
Category.add_category('新类别')

# 删除一个类别
Category.delete_category('新类别')

# 获取所有类别及其下的所有项目
categories = Category.get_all()
for category_title, items in categories.items():
    print(f'类别: {category_title}')
    for item in items:
        print(f'项目: {item["title"]}, 链接: {item["link"]}, logo: {item["logo"]}')

# 添加一个新的项目
Item.add_item('新类别', '新项目', 'http://example.com', 'http://example.com/logo.png')

# 删除一个项目
Item.delete_item('新项目')

# 更新一个项目
Item.update_item('新项目', '新项目2', 'http://example2.com', 'http://example2.com/logo.png')

# 获取一个项目
item = Item.get_item('新项目2')
if item:
    print(f'项目: {item.title}, 链接: {item.link}, logo: {item.logo}')

# 获取一个类别下的所有项目
items = Item.get_all(1)  # 假设类别ID为1
for item in items:
    print(f'项目: {item["title"]}, 链接: {item["link"]}, logo: {item["logo"]}')
'''
