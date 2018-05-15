# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""


from flask import Blueprint
from flask_restful import Api


api_bp = Blueprint('api', __name__)
api = Api(api_bp)

from .auth import Auth
api.add_resource(Auth, "/auth/")

from .product import Product
api.add_resource(Product, "/product/")

from .project import Project
api.add_resource(Project, "/project/")

from .suite import Suite
api.add_resource(Suite, "/suite/")

from .object import Object
api.add_resource(Object, "/object/")

from .case import Case
api.add_resource(Case, "/case/")

from .step import Step
api.add_resource(Step, "/step/")

from .var import Var
api.add_resource(Var, "/var/")

from .keyword import Keyword
api.add_resource(Keyword, "/keyword/")

from .help import Help
api.add_resource(Help, "/help/")

from .task import Task
api.add_resource(Task, "/task/")

from .trigger import Triggers
api.add_resource(Triggers, "/trigger/")

from .stats import Stats
api.add_resource(Stats, "/stats/")

from .user import Users
api.add_resource(Users, "/user/")

from .role import Roles
api.add_resource(Roles, "/role/")
