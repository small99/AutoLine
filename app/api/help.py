# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

from datetime import datetime
from flask import url_for
from flask_restful import Resource, reqparse
from ..utils.parsing import parser_doc


class Help(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()

    def get(self):

        args = self.parser.parse_args()

        return parser_doc()
