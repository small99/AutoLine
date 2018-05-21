# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import os
import re
import xml.etree.ElementTree as ET
from flask import render_template
from ..models import AutoSuite, AutoCase, AutoStep


class Report:

    def __init__(self, project_id, build_no):
        self.project_id = project_id
        self.build_no = build_no

    def build_report(self):

        return render_template('report.html',
                               project_id=self.project_id,
                               build_no=self.build_no,
                               summary=self.__parser_summary())

    def __parser_summary(self):
        summary = {}
        output_dir = os.getcwd() + "/logs/%s/%s" % (self.project_id, self.build_no)
        tree = ET.parse(output_dir + "/output.xml")
        root = tree.getroot()

        summary["generated"] = root.attrib["generated"]
        summary["generator"] = root.attrib["generator"]
        summary["name"] = root.find("./suite").attrib["name"]
        summary["build_no"] = self.build_no
        summary["starttime"] = root.find("./suite/status").attrib["starttime"]
        summary["endtime"] = root.find("./suite/status").attrib["endtime"]
        summary["status"] = root.find("./suite/status").attrib["status"]
        summary["pass"] = root.find("./statistics/suite/stat").attrib["pass"]
        summary["fail"] = root.find("./statistics/suite/stat").attrib["fail"]

        return summary

    def parser_detail_info(self):
        detail_data = []
        output_dir = os.getcwd() + "/logs/%s/%s" % (self.project_id, self.build_no)
        tree = ET.parse(output_dir + "/output.xml")
        root = tree.getroot()
        for test in root.iter("test"):
            detail_data.append({
                "status": test.find("status").attrib["status"].lower(),
                "name": test.attrib["name"].split(" ")[1],
                "starttime": test.find("status").attrib["starttime"],
                "endtime": test.find("status").attrib["endtime"]
            })
            for kw in test.iter("kw"):
                text = ""
                image = ""
                for msg in kw.iter("msg"):
                    if "<a" in msg.text:
                        img = re.findall('src="images/(.+)" width', msg.text)
                        if len(img) != 0:
                            image = img[0]
                    else:
                        text = text + msg.text + "<br>"
                #print(text)
                """    
                msg = kw.find("msg")
                if msg is not None:
                    text = kw.find("msg").text

                if "<a" in text:
                    image = re.findall('src="images/(.+)" width', text)[0]
                """
                detail_data.append({
                    "status": kw.find("status").attrib["status"].lower(),
                    "keyword": kw.attrib["name"],
                    "msg": text,
                    "image": image,
                    "project_id": self.project_id,
                    "build_no": self.build_no
                })

        return detail_data
