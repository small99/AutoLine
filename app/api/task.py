# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import os
import xml.etree.ElementTree as ET
from datetime import datetime
from flask import url_for
from flask_restful import Resource, reqparse
from sqlalchemy import and_
from flask_login import current_user

from ..models import AutoProject, AutoTask, User
from .. import db


class Task(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('project_id', type=int, default=-1)
        self.parser.add_argument('task_id', type=int, default=-1)
        self.parser.add_argument('page', type=int, default=1)
        self.parser.add_argument('rows', type=int, default=15)

    def get(self):
        args = self.parser.parse_args()
        if args["project_id"] == -1:
            pagination = AutoTask.query.order_by(AutoTask.id.desc()).paginate(
                args["page"], per_page=args["rows"],
                error_out=False
            )
        else:
            pagination = AutoTask.query.filter_by(project_id=args["project_id"]).order_by(AutoTask.id.desc()).paginate(
                args["page"], per_page=args["rows"],
                error_out=False
            )

        tasks = pagination.items
        data = {"total": pagination.total, "rows": []}
        urls = {
            "pass": "success.png",
            "fail": "fail.png",
            "running": "run.gif"
                }

        for task in tasks:
            status = self.__check_task_status(task.project_id, task.build_no)
            data["rows"].append({
                "id": task.id,
                "status": status,
                "url": url_for('static', filename='images/%s' % urls[status]),
                "name": AutoProject.query.filter_by(id=task.project_id).first().name,
                "build_no": task.build_no,
                "project_id": task.project_id,
                "cron": AutoProject.query.filter_by(id=task.project_id).first().cron,
                "start_time": task.create_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": task.end_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": "%s秒" % task.duration,
                "runner": User.query.filter_by(id=task.create_author_id).first().username
            })

        return data

    def __check_task_status(self, project_id, build_no):
        status = "running"
        output_dir = os.getcwd() + "/logs/%s/%s" % (project_id, build_no)
        if os.path.exists(output_dir + "/report.html"):
            task = AutoTask.query.filter(and_(AutoTask.project_id == project_id,
                                              AutoTask.build_no == build_no)).first()


            tree = ET.parse(output_dir + "/output.xml")
            root = tree.getroot()
            passed = root.find("./statistics/suite/stat").attrib["pass"]
            fail = root.find("./statistics/suite/stat").attrib["fail"]

            if int(fail) != 0:
                status = 'fail'
                task.status = 'fail'
            else:
                status = 'pass'
                task.status = 'pass'
            starttime = datetime.strptime(root.find("./suite/status").attrib["starttime"], "%Y%m%d %H:%M:%S.%f")
            endtime = datetime.strptime(root.find("./suite/status").attrib["endtime"], "%Y%m%d %H:%M:%S.%f")
            task.create_timestamp = starttime
            task.end_timestamp = endtime
            task.duration = (endtime - starttime).seconds
            task.status = status

            db.session.merge(task)
            db.session.commit()

        return status

