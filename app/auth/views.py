# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email


#@auth.before_app_request
#def before_request():
#    if not current_user.is_anonymous():
#        current_user.ping()


@auth.route('/login/', methods=['POST'])
def login():
    email = request.form["email"]
    password = request.form["password"]
    user = User.query.filter_by(email=email).first()

    if user is not None and user.verify_password(password):

        login_user(user, True)
        current_user.ping()

        return redirect(url_for("main.dashboard"))

    return render_template('index.html', user=user)

