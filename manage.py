# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import os
import sys
import codecs
import requests
from app import create_app, db
from app.utils.trigger import Trigger
from app.models import User, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


def check_python_version():
    if sys.version_info < (3, 4):
        print("请安装Python3.4及以上版本")
        exit(0)


def check_version():
    f = codecs.open('version.txt', 'r')
    version = f.readline()
    s = requests.Session()
    r_version = s.get("https://gitee.com/lym51/AutoLine/raw/master/version.txt").text
    if version != r_version:
        print("*" * 25)
        print("本地版本：v%s" % version)
        print("github版本: v%s" % r_version)
        print("AutoLine开源平台代码已有更新，请到下面的地址更新代码:")
        print("下载最新代码，直接覆盖本地即可")
        print("https://github.com/small99/AutoLine")
        print("*" * 25)
        exit(0)
    f.close()


def start_trigger():
    app.config["TRIGGER"] = Trigger(app)
    app.config["TRIGGER"].setup()
    app.config["TRIGGER"].load_job_list()
    app.config["TRIGGER"].start()


def output_logo():
    logo = """
    --------------------------------------------    
                            _       _             
       /\         _        | |     (_)            
      /  \  _   _| |_  ___ | |      _ ____   ____ 
     / /\ \| | | |  _)/ _ \| |     | |  _ \ / _  )
    | |__| | |_| | |_| |_| | |_____| | | | ( (/ / 
    |______|\____|\___)___/|_______)_|_| |_|\____)
    --------------------------------------------
    https://github.com/small99/AutoLine                                            
    """
    print(logo)

os.environ["PATH"] = os.environ["PATH"] + ";" + os.getcwd() + "/bin"

app = create_app(os.environ.get('AUTOBEAT_CONFIG') or 'default')
#trigger = Trigger(app)
#trigger.setup()
#trigger.load_job_list()

manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def deploy():
    from flask_migrate import upgrade
    from app.models import Role, User

    upgrade()

    Role.insert_roles()

    User.insert_admin()

    User.insert_auto()

    User.insert_user("lymking@foxmail.com", "lyy51", "Lym")


@manager.command
def keyword():
    import subprocess
    libs = ('BuiltIn', 'Collections', 'DateTime',
            'Dialogs', 'OperatingSystem', 'Process',
            'Screenshot', 'String', 'Telnet', 'XML',
            'RequestsLibrary', 'AppiumLibrary', 'SeleniumLibrary')
    print("生成关键字...")
    for lib in libs:
        args = 'python -m robot.libdoc %s doc/%s.xml' % (lib, lib)
        subprocess.call(args, shell=True)


if __name__ == '__main__':
    check_python_version()
    check_version()

    if "runserver" in sys.argv:
        start_trigger()

    output_logo()

    manager.run()
