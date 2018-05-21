# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import os
from datetime import datetime
from flask import url_for
from flask_restful import Resource, reqparse
from flask_login import current_user

from ..models import AutoProduct, AutoProject, AutoSuite, AutoObject, AutoCase, AutoVar, AutoStep, AutoTask, User
from .. import db


class Stats(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('category', type=str)

    def get(self):
        args = self.parser.parse_args()
        category = args["category"].lower()
        if category == "project_stats":
            return self.__project_stats()
        elif category == "task_stats":
            return self.__task_stats()
        elif category == "exec_stats":
            return self.__exec_stats()

    def __task_stats(self):
        stat = {"data": [], "label": []}
        # 统计项目的任务数
        projects = AutoProject.query.all()
        for p in projects:
            stat["label"].append(p.name)
            stat["data"].append(AutoTask.query.filter_by(project_id=p.id).count())

        return stat

    def __project_stats(self):
        stat = {"data": [], "label": []}
        # 按产品分类统计项目数
        products = AutoProduct.query.all()
        for p in products:
            stat["label"].append(p.name)
            stat["data"].append(AutoProject.query.filter_by(product_id=p.id).count())

        return stat

    def __exec_stats(self):
        stat = {"data": [], "label": []}
        stat["data"].append(AutoTask.query.filter_by(status="pass").count())
        stat["label"].append("通过")

        stat["data"].append(AutoTask.query.filter_by(status="running").count())
        stat["label"].append("运行中")

        stat["data"].append(AutoTask.query.filter_by(status="fail").count())
        stat["label"].append("失败")

        stat["data"].append(AutoTask.query.filter_by(status="exception").count())
        stat["label"].append("异常")

        return stat