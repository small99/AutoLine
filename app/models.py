# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""


from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from . import db, login_manager


class Permission:
    """
        权限
    """
    GUEST = 1
    PROJECT = 2
    MANAGER = 4
    ADMINISTRATOR = 16


class Role(db.Model):
    """
        角色
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            '普通用户': [Permission.GUEST],
            '项目管理': [Permission.GUEST, Permission.PROJECT],
            '管理员': [Permission.GUEST, Permission.PROJECT, Permission.MANAGER],
            '超级管理员': [Permission.GUEST, Permission.PROJECT, Permission.MANAGER, Permission.ADMINISTRATOR]
        }

        default_role = '普通用户'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    """
        用户
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.now())
    last_seen = db.Column(db.DateTime(), default=datetime.now())

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='超级管理员').first()
            if self.role is None:
                self.role = Role.query.filter_by(id=self.role_id).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)

        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def insert_admin():
        email = current_app.config["FLASKY_ADMIN"]
        user = User.query.filter_by(email=email).first()
        if user is None:
            role = Role.query.filter_by(name='超级管理员').first()
            u = User(email=email, username="AutoLine", name="AutoLine", role_id=role.id, password="123456")
            db.session.add(u)
            db.session.commit()

    @staticmethod
    def insert_auto():
        role = Role.query.filter_by(name='项目管理').first()
        u = User(email="AutoExecutor@autoline.com", username="AutoExecutor", name="AutoExecutor", role_id=role.id, password="123456")
        db.session.add(u)
        db.session.commit()

    @staticmethod
    def insert_user(email, name, username, password="123456", role_name='普通用户'):
        user = User.query.filter_by(email=email).first()
        if user is None:
            role = Role.query.filter_by(name=role_name).first()
            u = User(email=email, username=username, name=name, role_id=role.id, password=password)
            db.session.add(u)
            db.session.commit()

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        user = User.query.get(data.get('reset'))
        if user is None:
            return False

        user.password = new_password
        db.session.add(user)

        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)

        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        if data.get('change_email') != self.id:
            return False

        new_email = data.get('new_email')
        if new_email is None:
            return False

        if self.query.filter_by(email=new_email).first() is not None:
            return False

        self.email = new_email
        db.session.add(self)

        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMINISTRATOR)

    def is_anonymous(self):
        return False

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)

    def to_json(self):
        json_user = {
            'username': self.username,
            'name': self.name,
            'role_id': self.role_id,
            'member_since': self.member_since,
            'last_seen': self.last_seen
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)

        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None

        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AutoProduct(db.Model):
    """
        产品
    """
    __tablename__ = "auto_product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    desc = db.Column(db.String(128), index=True)
    tags = db.Column(db.String(64), index=True)
    enable = db.Column(db.Boolean, default=True, index=True)

    create_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    update_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    update_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())


class AutoProject(db.Model):
    """
        项目
    """
    __tablename__ = "auto_project"
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(64), index=True)
    product_id = db.Column(db.Integer)
    #product_id = db.Column(db.Integer, db.ForeignKey('auto_product.id'))
    name = db.Column(db.String(64), index=True)
    desc = db.Column(db.String(128), index=True)
    tags = db.Column(db.String(64), index=True)
    enable = db.Column(db.Boolean, default=True, index=True)
    version = db.Column(db.String(32), index=True)
    cron = db.Column(db.Text)
    setup = db.Column(db.Text)
    teardown = db.Column(db.Text)

    create_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    update_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    update_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())


class AutoSuite(db.Model):
    """
        套件
    """
    __tablename__ = "auto_suite"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer)
    #project_id = db.Column(db.Integer, db.ForeignKey('auto_project.id'))
    prev = db.Column(db.Integer)  # 兄Suite id
    name = db.Column(db.String(64), index=True)
    desc = db.Column(db.String(128), index=True)
    tags = db.Column(db.String(64), index=True)
    enable = db.Column(db.Boolean, default=True, index=True)
    setup = db.Column(db.Text)
    teardown = db.Column(db.Text)

    create_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    update_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    update_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())


class AutoCase(db.Model):
    """
        用例
    """
    __tablename__ = "auto_case"
    id = db.Column(db.Integer, primary_key=True)
    suite_id = db.Column(db.Integer)
    #suite_id = db.Column(db.Integer, db.ForeignKey('auto_suite.id'))
    prev = db.Column(db.Integer)  # 兄Case id
    name = db.Column(db.String(64), index=True)
    desc = db.Column(db.String(128), index=True)
    tags = db.Column(db.String(64), index=True)
    enable = db.Column(db.Boolean, default=True, index=True)
    setup = db.Column(db.Text)
    teardown = db.Column(db.Text)

    create_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    update_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    update_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())


class AutoStep(db.Model):
    """
        步骤
    """
    __tablename__ = "auto_step"
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer)
    #case_id = db.Column(db.Integer, db.ForeignKey('auto_case.id'))
    prev = db.Column(db.Integer)  # 兄Step id
    enable = db.Column(db.Boolean, default=True, index=True)
    desc = db.Column(db.String(128), index=True)
    keyword = db.Column(db.String(128), index=True)
    param_1 = db.Column(db.String(128), index=True)
    param_2 = db.Column(db.String(128), index=True)
    param_3 = db.Column(db.String(128), index=True)
    param_4 = db.Column(db.String(128), index=True)
    step = db.Column(db.Text)

    create_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    update_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    update_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())


class AutoObject(db.Model):
    """
        对象库套件
    """
    __tablename__ = "auto_object"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer)
    #project_id = db.Column(db.Integer, db.ForeignKey('auto_project.id'))
    category = db.Column(db.String(64), index=True)
    prev = db.Column(db.Integer)  # 兄对象 id
    name = db.Column(db.String(64), index=True)
    desc = db.Column(db.String(128), index=True)
    tags = db.Column(db.String(64), index=True)
    enable = db.Column(db.Boolean, default=True, index=True)
    setup = db.Column(db.Text)
    teardown = db.Column(db.Text)

    create_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    update_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    update_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())


class AutoKeyword(db.Model):
    """
        关键字
    """
    __tablename__ = "auto_keyword"
    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer)
    #object_id = db.Column(db.Integer, db.ForeignKey('auto_object.id'))
    prev = db.Column(db.Integer)  # 兄keyword id
    keyword = db.Column(db.Text)

    create_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    update_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    update_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())


class AutoElement(db.Model):
    """
        元素
    """
    __tablename__ = "auto_element"
    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer)
    #object_id = db.Column(db.Integer, db.ForeignKey('auto_object.id'))
    prev = db.Column(db.Integer)  # 兄keyword id
    element = db.Column(db.Text)

    create_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    update_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    update_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())


class AutoVar(db.Model):
    """
        变量
    """
    __tablename__ = "auto_variable"
    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer)
    #object_id = db.Column(db.Integer, db.ForeignKey('auto_object.id'))
    prev = db.Column(db.Integer)  # 兄keyword id
    category = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64), index=True)
    desc = db.Column(db.String(128), index=True)
    value = db.Column(db.Text)

    create_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    update_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    update_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class AutoTask(db.Model):
    """
        任务
    """
    __tablename__ = "auto_task"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer)
    #project_id = db.Column(db.Integer, db.ForeignKey('auto_project.id'))
    build_no = db.Column(db.Integer, index=True)
    status = db.Column(db.String(32), index=True)
    result = db.Column(db.String(32), index=True)
    duration = db.Column(db.Integer)
    create_author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    end_timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
