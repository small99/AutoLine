# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import os
import codecs
from datetime import datetime
from flask import current_app
from flask_login import current_user
from sqlalchemy import and_
#from robot.api import TestSuiteBuilder, TestSuite, ResultWriter, TestData, TestCaseFile, ResourceFile
from .. import db
from ..models import AutoProject, AutoSuite, AutoObject, AutoCase, AutoStep, AutoVar, AutoTask


class Builder:
    def __init__(self, id):
        self.id = id
        #self.category = category
        self.root = os.getcwd()
        self.project_dir = 0
        self.build_no = 1
        self.project_name = ""
        self.task_dir = ""
        self.has_case = False

    def build(self):
        self.build_task()

        self.build_variables()

        self.build_suites()

    def build_task(self):

        project = AutoProject.query.filter_by(id=self.id).first()
        if project:
            #self.suite = TestSuite(name=project.name, doc=project.desc)
            self.project_dir = self.root + '/logs/%d' % project.id
            self.project_dir = self.project_dir.replace("\\", "/")
            self.project_name = project.name

            if os.path.exists(self.project_dir) is False:
                os.makedirs(self.project_dir)
            L = []
            dirs = os.listdir(self.project_dir)

            for d in dirs:
                if d.isdigit():
                    L.append(int(d))

            L.sort()

            # 创建当前测试项目build no.
            self.build_no = 1
            if len(L) != 0:
                self.build_no = int(L[-1]) + 1

            task_dir = self.project_dir + "/%d" % self.build_no
            os.makedirs(task_dir)

    def build_variables(self):
        obj_dir = self.project_dir + "/%d" % self.build_no
        obj_dir = obj_dir.replace("\\", "/")
        resource_path = obj_dir + "/resource.txt"
        resource_path = resource_path.replace("\\", "/")
        #resource_file = codecs.open(resource_path, 'w', 'UTF-8')
        resource_file = codecs.open(resource_path, 'w', "utf-8")
        resource_file.write("*** Variables ***\n")
        objects = AutoObject.query.filter_by(project_id=self.id).order_by(AutoObject.id.asc()).all()
        for obj in objects:
            variables = AutoVar.query.filter_by(object_id=obj.id).order_by(AutoVar.id.asc()).all()
            for var in variables:
                resource_file.write("%s    %s\n" % (var.name, var.value))

            resource_file.write("\n\n")

        resource_file.close()

    def build_suites(self):
        suite_dir = self.project_dir + "/%d" % self.build_no
        suite_dir = suite_dir.replace("\\", "/")
        # 截图目录
        images_dir = os.path.normpath(suite_dir + "/images")
        images_dir = images_dir.replace("\\", "/")
        if os.path.exists(images_dir) is False:
            os.makedirs(images_dir)

        case_path = suite_dir + "/testcase.robot"
        case_file = codecs.open(case_path, 'w', "utf-8")
        #case_file = codecs.open(case_path, 'w', 'UTF-8')

        # 写settings
        libs = ('Collections', 'DateTime',
                'Dialogs', 'OperatingSystem', 'Process',
                'Screenshot', 'String', 'Telnet', 'XML')

        case_file.write("*** Settings ***\n")
        for lib in libs:
            case_file.write("Library\t%s\n" % lib)

        project = AutoProject.query.filter_by(id=self.id).first()
        auto_lib = {"web": 'SeleniumLibrary',
                    "app": 'AppiumLibrary',
                    "http": 'RequestsLibrary'}
        if project:
            case_file.write("Library\t%s\n" % auto_lib[project.category])

        case_file.write("\nResource\tresource.txt\n")
        case_file.write("\nSuite Setup  Screenshot.Set Screenshot Directory\t%s\n" % images_dir)
        if project.category == "web":
            case_file.write("\nSuite Teardown  SeleniumLibrary.Close All Browsers\n\n")

        case_file.write("*** Test Cases ***\n\n")
        suites = AutoSuite.query.filter_by(project_id=self.id).order_by(AutoSuite.id.asc()).all()
        for suite in suites:
            cases = AutoCase.query.filter_by(suite_id=suite.id).order_by(AutoCase.id.asc()).all()
            for case in cases:
                case_file.write("%d-%d %s.%s\n" % (suite.id, case.id, suite.name, case.name))
                steps = AutoStep.query.filter_by(case_id=case.id).order_by(AutoStep.id.asc()).all()
                for step in steps:
                    self.has_case = True
                    case_file.write("\t%s\t%s\t%s\t%s\t%s\n" % (
                        step.keyword,
                        step.param_1, step.param_2, step.param_3, step.param_4
                    ))

            case_file.write("\n\n")

        case_file.close()

    def has_test_case(self):

        return self.has_case

    """
    def test_run(self, app, user_id):
        with app.app_context():
            try:
                task = AutoTask(project_id=self.id,
                                build_no=self.build_no,
                                status="running",
                                create_author_id=user_id)
                db.session.add(task)
                db.session.commit()
                base_dir = self.project_dir + "/%d/" % self.build_no
                test_suite = TestSuiteBuilder().build(base_dir + "testcase.robot")
                test_suite.name = self.project_name

                result = test_suite.run(output=base_dir + "/result/output.xml")

                # Report and xUnit files can be generated based on the result object.
                ResultWriter(result).write_results(report=base_dir + "/result/result.html",
                                                   log=base_dir + "/result/log.txt")

                # Generating log files requires processing the earlier generated output XML.
                ResultWriter(base_dir + "/result/output.xml").write_results()

                task = AutoTask.query.filter(and_(AutoTask.project_id == self.id,
                                                     AutoTask.build_no == self.build_no)).first()
                task.end_timestamp = datetime.utcnow()
                stats = result.statistics
                if stats.total.critical.failed != 0:
                    task.status = 'fail'
                else:
                    task.status = 'pass'

                db.session.merge(task)
                db.session.commit()
            except Exception as e:
                print(str(e))
                return str(e)

        return None
    """
