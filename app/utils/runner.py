# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import os
import platform
import codecs
import time
import json
import subprocess
from datetime import datetime
from threading import Thread, Timer
import xml.etree.ElementTree as ET
from flask import current_app
from flask_login import current_user
from sqlalchemy import and_
from ..models import AutoTask, AutoProject, User
from .. import db
from ..auto.builder import Builder
from .process import Process


def robot_run(category, id):
    app = current_app._get_current_object()
    if len(app.config["RESULTS"]) > int(app.config['AUTO_PROCESS_COUNT']):
        return json.dumps({"status": "busying", "msg": "任务池已满！！！"})

    builder = Builder(category, id)
    builder.build()
    app.config["RESULTS"].append(app.config["POOL"].apply_async(builder.test_run, (app, current_user.get_id(),)))

    # app.config["POOL"].join()

    return json.dumps({"status": "success", "msg": "任务启动成功"})


def robot_async_run(category, id):
    app = current_app._get_current_object()

    builder = Builder(category, id)
    builder.build()

    thr = Thread(target=builder.test_run, args=[app, current_user.get_id()])
    #app.config["RESULTS"].append(thr)

    thr.start()

    return json.dumps({"status": "success", "msg": "任务启动成功"})


def check_process_status(app):
    print("timer to check ....%d" % len(app.config["RUNNERS"]))
    with app.app_context():

        try:
            for runner in app.config["RUNNERS"]:
                if runner.is_finish():
                    runner.write_result()
                    app.config["RUNNERS"].remove(runner)
        except Exception as e:
            print(e)


def debug_run(id):
    builder = Builder(id)
    builder.build()
    runner = Runner(builder.id, builder.build_no)

    runner.debug()

    return (builder.id, builder.build_no)


def run_process(category, id):
    builder = Builder(id)
    builder.build()

    if builder.has_test_case():

        runner = Runner(builder.id, builder.build_no)
        if category == "auto":
            runner.auto_run()
        else:
            runner.run()

        app = current_app._get_current_object()

        app.config["TRIGGER"].update_job(id)

        app.config["RUNNERS"].append({
            "project_id": builder.id,
            "task_id": builder.build_no,
            "runner": runner
        })

        return json.dumps({"status": "success", "msg": "任务启动成功"})
    else:
        return json.dumps({"status": "fail", "msg": "项目中没有创建关键字步骤，任务启动失败，请新增关键字步骤！！！"})


class Runner:
    def __init__(self, project_id, build_no):
        self.project_id = project_id
        self.build_no = build_no
        self._process = None
        self._timer = None
        self._out_fd = None

    def auto_run(self):
        try:
            user_id = User.query.filter_by(username="AutoExecutor").first().id
            name = AutoProject.query.filter_by(id=self.project_id).first().name
            task = AutoTask(project_id=self.project_id,
                            build_no=self.build_no,
                            status="running",
                            create_author_id=user_id,
                            create_timestamp=datetime.now())
            db.session.add(task)
            db.session.commit()

            output_dir = os.getcwd() + "/logs/%s/%s" % (self.project_id, self.build_no)
            output_dir = output_dir.replace("\\", "/")

            # -x result/output.xml -l result/log.html -r result/report.html
            shell = False
            if "Windows" in platform.platform():
                self._out_fd = codecs.open(output_dir + "/logs.log", "a+", "cp936")
                command = "pybot -d %s -L DEBUG -N %s %s/testcase.robot" % (output_dir, name, output_dir)
                shell = True
            else:
                self._out_fd = codecs.open(output_dir + "/logs.log", "a+", "utf-8")
                command = ["pybot", "-d", "%s" % output_dir, "-L", "DEBUG", "-N", "%s" % name, "%s/testcase.robot" % output_dir]
                #print(command)

            self._process = subprocess.Popen(command, shell=shell, stdout=self._out_fd, stderr=subprocess.STDOUT)
            #self._process = Process(command)

            #self._process.start()

        except Exception as e:
            print(str(e))
            pass

        return {"status": "success",
                "msg": "任务启动成功",
                "project_id": self.project_id,
                "build_no": self.build_no}

    def run(self):
        #
        try:
            name = AutoProject.query.filter_by(id=self.project_id).first().name
            task = AutoTask(project_id=self.project_id,
                            build_no=self.build_no,
                            status="running",
                            create_author_id=current_user.get_id(),
                            create_timestamp=datetime.now())
            db.session.add(task)
            db.session.commit()

            output_dir = os.getcwd() + "/logs/%s/%s" % (self.project_id, self.build_no)
            output_dir = output_dir.replace("\\", "/")

            shell = False
            if "Windows" in platform.platform():
                self._out_fd = codecs.open(output_dir + "/logs.log", "a+", "cp936")
                command = "pybot -d %s -L DEBUG -N %s %s/testcase.robot" % (output_dir, name, output_dir)
                shell = True
            else:
                self._out_fd = codecs.open(output_dir + "/logs.log", "a+", "utf-8")
                command = ["pybot", "-d", "%s" % output_dir, "-L", "DEBUG", "-N", "%s" % name,
                           "%s/testcase.robot" % output_dir]
                # print(command)

            self._process = subprocess.Popen(command, shell=shell, stdout=self._out_fd, stderr=subprocess.STDOUT)

        except Exception as e:
            print(str(e))
            pass

        return {"status": "success",
                "msg": "任务启动成功",
                "project_id": self.project_id,
                "build_no": self.build_no}

    def debug(self):
        try:
            output_dir = os.getcwd() + "/logs/%s/%s" % (self.project_id, self.build_no)
            output_dir = output_dir.replace("\\", "/")
            # -x result/output.xml -l result/log.html -r result/report.html
            command = ["pybot", "-d", "%s" % output_dir, "--dryrun", "-N", "调试输出", "%s/testcase.robot" % output_dir]
            self._out_fd = open(output_dir + "/debug.log", "a+")
            self._process = subprocess.Popen(command, shell=False, stdout=self._out_fd, stderr=subprocess.STDOUT)
            while True:
                if self._process.poll() == 0:  # 判断子进程是否结束
                    break
                else:
                    time.sleep(0.2)

        except Exception as e:
            print(str(e))
            pass

        return {"status": "success",
                "msg": "任务启动成功",
                "project_id": self.project_id,
                "build_no": self.build_no}

    def stop(self):
        status = "success"
        msg = "任务终止"
        try:
            self._process.stop()
            msg += "成功"
        except Exception as e:
            status = "fail"
            msg = msg + "异常" + str(e)

        return {"status": status,
                "msg": msg,
                "project_id": self.project_id,
                "build_no": self.build_no}

    def get_output(self, wait_until_finished=False):
        return self._process.get_output(wait_until_finished)

    def is_finish(self):
        return self._process.is_finished()

    def write_result(self):
        output_dir = os.getcwd() + "/logs/%s/%s" % (self.project_id, self.build_no)
        output_dir = output_dir.replace("\\", "/")
        print("write ... result ...")
        print(os.path.exists(output_dir + "/log.html"))
        if os.path.exists(output_dir + "/log.html"):
            time.sleep(0.2)
            task = AutoTask.query.filter(and_(AutoTask.project_id == self.project_id,
                                              AutoTask.build_no == self.build_no)).first()
            tree = ET.parse(output_dir + "/output.xml")
            root = tree.getroot()
            passed = root.find("./statistics/suite/stat").attrib["pass"]
            fail = root.find("./statistics/suite/stat").attrib["fail"]
            if int(fail) != 0:
                task.status = 'fail'
            else:
                task.status = 'pass'
            db.session.merge(task)
            db.session.commit()

            self._timer.canel()
