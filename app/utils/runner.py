# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import os
import time
import json
from datetime import datetime
from threading import Thread, Timer
import xml.etree.ElementTree as ET
from flask import current_app
from flask_login import current_user
from sqlalchemy import and_
from ..models import AutoTask, AutoProject
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


def run_process(id):
    from ..utils.runner import Runner
    builder = Builder(id)
    builder.build()

    runner = Runner(builder.id, builder.build_no)

    runner.run()

    app = current_app._get_current_object()

    app.config["TRIGGER"].update_job(id)

    # app.config["RUNNERS"].append(runner)

    return json.dumps({"status": "success", "msg": "任务启动成功"})


class Runner:
    def __init__(self, project_id, build_no):
        self.project_id = project_id
        self.build_no = build_no
        self._process = None
        self._timer = None

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
            # -x result/output.xml -l result/log.html -r result/report.html
            command = ["pybot", "-d", "%s" % output_dir, "-N", "%s" % name,"%s/testcase.robot" % output_dir]

            self._process = Process(command)

            self._process.start()

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
