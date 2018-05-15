# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import os

from flask import render_template, send_file
from flask_login import login_required, current_user, logout_user

from . import main

from ..utils.runner import run_process
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


#@login_required
@main.route('/test_run/<category>/<id>', methods=['GET'])
def test_run(category, id):
    status = run_process(id)

    return status


@login_required
@main.route('/report/<project_id>/<build_no>', methods=['GET'])
def report(project_id, build_no):
    r = Report(project_id, build_no)

    return r.build_report()

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

    return send_file(img_path)
