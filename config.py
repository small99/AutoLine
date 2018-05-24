# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import os
import random
import codecs

basedir = os.path.abspath(os.path.dirname(__file__))

choice = ("QWERTYUIOPASDFGHJKLMNBVCXZqazxswedcvfrtgbnhyujmkiolp1234567890!@#$%^&*")


class Config:
    if os.path.exists('.env'):
        print('Import environment from .env')
        for line in codecs.open('.env'):
            var = line.strip().split('=')
            if len(var) == 2:
                os.environ[var[0]] = var[1]
                #print(var[0] + "=" + var[1])

    SECRET_KEY = os.environ.get('SECRET_KEY')# or random.choices(choice, k=16)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.126.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = os.environ.get('FLASKY_MAIL_SUBJECT_PREFIX')
    FLASKY_MAIL_SENDER = os.environ.get('FLASKY_MAIL_SENDER')
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SSL_REDIRECT = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30
    FLASKY_SLOW_DB_QUERY_TIME = 0.5

    # 自定义参数
    AUTO_LOGS = os.environ.get('AUTO_LOGS')
    AUTO_REPORT = os.environ.get('AUTO_REPORT')

    RUNNERS = []
    TRIGGER = None

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'AutoLine-dev.sqlite') #os.environ.get('DEV_DATABASE_URL')
    TRIGGER_DATABASE_URL = 'sqlite:///' + os.path.join(basedir, 'AutoLine-dev.sqlite')


class ProductionConfig(Config):
    #DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') + "?charset=utf8" # or 'sqlite:///' + os.path.join(basedir, 'AutoLine.sqlite')
    #SQLALCHEMY_ECHO = True
    TRIGGER_DATABASE_URL = os.environ.get('TRIGGER_DATABASE_URL')


    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # 发送初始化错误信息给管理员
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()

        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' AutoLine Startup Error',
            credentials=credentials,
            secure=secure)

        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,

    "default": DevelopmentConfig
}
