# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

from datetime import datetime
from flask import url_for
from flask_restful import Resource, reqparse
from flask_login import current_user

from ..models import Role
from .. import db


class Roles(Resource):
    def __init__(self):
        pass

    def get(self):
        data = {"rows": []}
        roles = Role.query.all()
        for r in roles:
            data["rows"].append({
                "id": r.id,
                "名称": r.name
            })

        return data
