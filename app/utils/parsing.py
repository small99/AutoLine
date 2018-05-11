# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import os
import xml.etree.ElementTree as ET


def parser():
    keyword_list = []
    cwd = os.getcwd() + "/doc"
    keys = os.listdir(cwd)
    for k in keys:
        path = cwd + '/%s' % k
        tree = ET.parse(path)
        root = tree.getroot()
        name = root.attrib["name"]
        children = []
        for kw in root.iter("kw"):
            # 关键字
            keyword = name + "." + kw.attrib["name"]

            # 关键字参数
            params = []
            for arg in kw.iter("arg"):
                params.append(arg.text)

            # 使用说明
            doc = kw.find("doc").text

            children.append({
                "id": name + keyword,
                "text": keyword,
                "attributes": {
                    "params": params,
                    "doc": doc
                }
            })

        keyword_list.append({
            "id": name,
            "text": name,
            "state": "closed",
            "children": children
        })

    return keyword_list
