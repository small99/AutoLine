# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import os
import platform
import codecs
from flask import render_template, send_file, current_app
from flask_login import login_required, current_user, logout_user

from . import main

from ..utils.runner import run_process, debug_run
from ..utils.report import Report

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@login_required
@main.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html', user=current_user)

@login_required
@main.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return render_template('index.html')


@login_required
@main.route('/user', methods=['GET'])
def user():
    return render_template('user.html', user=current_user)


@login_required
@main.route('/help', methods=['GET'])
def help():
    return render_template('help.html')

@login_required
@main.route('/product', methods=['GET'])
def product():
    return render_template('product.html', user=current_user)


@login_required
@main.route('/project', methods=['GET'])
def project():
    return render_template('project.html', user=current_user)


@login_required
@main.route('/task/<id>', methods=['GET'])
def task(id):
    return render_template('task.html', id=id)

@login_required
@main.route('/task_list', methods=['GET'])
def task_list():
    return render_template('task_list.html')

@login_required
@main.route('/manage/<category>/<id>', methods=['GET'])
def manage(category, id):
    return render_template('%s.html' % category, id=id)


@login_required
@main.route('/test_run/<category>/<id>', methods=['GET'])
def test_run(category, id):

    status = run_process(category, id)

    return status


@main.route('/debug/<id>', methods=['GET'])
def debug(id):
    project_id, build_no = debug_run(id)
    log_path = os.getcwd() + "/logs/%s/%s/debug.log" % (project_id, build_no)
    logs = "还没捕获到调试信息^_^"
    if os.path.exists(log_path):
        f = codecs.open(log_path, "r", "utf-8")
        logs = f.read()
        f.close()

    return render_template('debug.html', logs=logs)


@login_required
@main.route('/report/<project_id>/<build_no>', methods=['GET'])
def report(project_id, build_no):
    r = Report(project_id, build_no)

    return r.build_report()


@login_required
@main.route('/run_logs/<project_id>/<build_no>', methods=['GET'])
def run_logs(project_id, build_no):
    log_path = os.getcwd() + "/logs/%s/%s/logs.log" % (project_id, build_no)
    log_path = log_path.replace("\\", "/")
    logs = "还没捕获到日志信息^_^"
    if os.path.exists(log_path):
        if "Windows" in platform.platform():
            f = codecs.open(log_path, "r", "cp936")
        else:
            f = codecs.open(log_path, "r", "utf-8")

        logs = f.read()
        #print(logs)
        f.close()
        """
        app = current_app._get_current_object()
        for r in app.config["RUNNERS"]:
            p = r["runner"]
            if p._process.returncode == 0:
                print('Subprogram success')
                app.config["RUNNERS"].remove(r)
        """

    return render_template('logs.html', logs=logs)

@login_required
@main.route('/detail/<project_id>/<build_no>', methods=['POST'])
def detail(project_id, build_no):
    r = Report(project_id, build_no)
    import json
    return json.dumps(r.parser_detail_info())


@login_required
@main.route('/view_image/<project_id>/<build_no>/<filename>', methods=['GET'])
def view_image(project_id, build_no, filename):

    img_path = os.getcwd() + "/logs/%s/%s/images/%s" % (project_id, build_no, filename)
    img_path.replace("\\", "/")
    if os.path.exists(img_path):
        return send_file(img_path)

    return "截图失败，木有图片!!!"
