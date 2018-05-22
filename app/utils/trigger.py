# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import os
import xml.etree.ElementTree as ET
from apscheduler.schedulers.background import BackgroundScheduler
from flask import url_for
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.sql import func
from dateutil import tz
from ..auto.executor import run_job
from ..models import AutoProject, AutoTask


class Trigger:

    def __init__(self, app):
        self.scheduler = None
        self.app = app

    def setup(self):
        self.scheduler = BackgroundScheduler({
            'apscheduler.jobstores.default': {
                'type': 'sqlalchemy',
                'url': self.app.config["TRIGGER_DATABASE_URL"] #os.environ.get('TRIGGER_DATABASE_URL')
            },
            'apscheduler.executors.processpool': {
                'type': 'threadpool',
                'max_workers': '30'
            },
            'apscheduler.job_defaults.coalesce': 'false',
            'apscheduler.job_defaults.max_instances': '4',
            'apscheduler.timezone': 'UTC',
        })

    def start(self):

        self.scheduler.start()

    def is_running(self):
        return self.scheduler.running()

    def shutdown(self):
        self.scheduler.shutdown()

    def load_job_list(self):
        with self.app.app_context():
            projects = AutoProject.query.all()
            # key_list = ("minute", "hour", "day", "month", "day_of_week")

            for p in projects:
                if p.enable and self.scheduler.get_job(p.id) is None:
                    cron = p.cron.replace("\n", "").strip().split(" ")
                    #print(cron)
                    if len(cron) < 5:
                        continue
                    j = self.scheduler.add_job(func=run_job, trigger='cron', name=p.name, replace_existing=True,
                                               minute=cron[0], hour=cron[1], day=cron[2], month=cron[3], day_of_week=cron[4],
                                               id="%s" % p.id, args=(p.id,))
                else:
                    self.update_job(p.id)

    def add_job(self, func, name, id, cron):
        if self.scheduler.get_job(id) is None:
            self.scheduler.add_job(func=func, trigger='cron', name=name,
                                   minute=cron[0],
                                   hour=cron[1],
                                   day=cron[2],
                                   month=cron[3],
                                   day_of_week=cron[4],
                                   id="%s" % id)

    def update_job(self, id):
        with self.app.app_context():
            p = AutoProject.query.filter_by(id=id).first()
            if p.enable:
                cron = p.cron.replace("\n", "").strip().split(" ")
                if len(cron) < 5:
                    return False
                print(self.scheduler.get_job(id))

                if self.scheduler.get_job(id) is None:
                    self.scheduler.add_job(func=run_job, trigger='cron', name=p.name,
                                           minute=cron[0], hour=cron[1], day=cron[2], month=cron[3], day_of_week=cron[4],
                                           id="%s" % id, args=(id,))
                else:
                    self.remove_job(id)

                    self.scheduler.add_job(func=run_job, trigger='cron', name=p.name,
                                           minute=cron[0], hour=cron[1], day=cron[2], month=cron[3], day_of_week=cron[4],
                                           id="%s" % id, args=(id,))

            return True

    def remove_job(self, id):
        if self.scheduler.get_job(id) is not None:
            self.scheduler.remove_job(id)

    def pause_job(self, id):
        pass

    def resume_job(self, id):
        pass

    def get_jobs(self):
        to_zone = tz.gettz("CST")
        #jobs = self.scheduler.get_jobs()
        urls = {
            "pass": "success.png",
            "fail": "fail.png",
            "running": "run.gif",
            "none": "project.png"
        }
        projects = AutoProject.query.order_by(AutoProject.id.desc()).all()
        data = {"total": len(projects), "rows": []}

        for p in projects:
            next_run_time = "调度未启动"
            status = "pass"
            job = self.scheduler.get_job(p.id)
            if job is not None:
                next_run_time = job.next_run_time.astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S")

                # 获取该job下最后一次运行状态
                task = AutoTask.query.filter_by(project_id=job.id).order_by(AutoTask.build_no.desc()).first()
                if task is not None:
                    output_dir = os.getcwd() + "/logs/%s/%s" % (task.project_id, task.build_no)
                    if os.path.exists(output_dir + "/report.html"):
                        tree = ET.parse(output_dir + "/output.xml")
                        root = tree.getroot()
                        # passed = root.find("./statistics/suite/stat").attrib["pass"]
                        fail = root.find("./statistics/suite/stat").attrib["fail"]
                        if int(fail) != 0:
                            status = 'fail'
                        else:
                            status = 'pass'
            else:
                status = "none"

            data["rows"].append({"id": "%s" % p.id,
                                 "name": p.name,
                                 "enable": p.enable,
                                 "status": status,
                                 "url": url_for('static', filename='images/%s' % urls[status]),
                                 "cron": p.cron,
                                 "next_run_time": next_run_time
                                 })

        """
        for job in jobs:
            status = "running"
            task = AutoTask.query.filter_by(project_id=job.id).order_by(AutoTask.build_no.desc()).first()
            if task is None:
                continue

            output_dir = os.getcwd() + "/logs/%s/%s" % (task.project_id, task.build_no)
            if os.path.exists(output_dir + "/report.html"):
                tree = ET.parse(output_dir + "/output.xml")
                root = tree.getroot()
                #passed = root.find("./statistics/suite/stat").attrib["pass"]
                fail = root.find("./statistics/suite/stat").attrib["fail"]
                if int(fail) != 0:
                    status = 'fail'
                else:
                    status = 'pass'

            data["rows"].append({"id": "%s" % job.id,
                                 "name": job.name,
                                 "status": status,
                                 "url": url_for('static', filename='images/%s' % urls[status]),
                                 "cron": AutoProject.query.filter_by(id=job.id).first().cron,
                                 "next_run_time": job.next_run_time.astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S")
                                 })
        """

        return data

    def print_jobs(self):
        pass
