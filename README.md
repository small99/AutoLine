# AutoLine开源平台
<!-- TOC -->

- [AutoLine开源平台](#autoline开源平台)
    - [什么是AutoLine开源平台](#什么是autoline开源平台)
    - [为什么要开发AutoLine](#为什么要开发autoline)
    - [特色](#特色)
    - [采用了哪些开源技术/框架](#采用了哪些开源技术框架)
    - [Mysql安装与配置](#mysql安装与配置)
    - [AutoLine下载及安装依赖](#autoline下载及安装依赖)
    - [配置文件说明](#配置文件说明)
    - [初始化及运行](#初始化及运行)
    - [外网访问运行方式](#外网访问运行方式)
    - [如何支持不同的浏览器](#如何支持不同的浏览器)
    - [截图](#截图)
    - [支持与联系](#支持与联系)
    - [许可](#许可)
    - [公众号](#公众号)

<!-- /TOC -->

## 什么是AutoLine开源平台

AutoLine开源平台是一个开源自动化测试解决方案，基于RobotFramework进行二次开发，支持RobotFramework几乎所有的库。

免安装版下载: [百度网盘下载](https://pan.baidu.com/s/1HyKykRRcXnu6K6V-8chDaQ)
![网盘图片](app/static/images/demo/pan.baidu.png)

用户简明教程： [简明教程](https://github.com/small99/AutoLine/blob/master/User%20Guide/User%20Guide/使用简明教程.md)

安装部署教程： [安装教程](https://github.com/small99/AutoLine/blob/master/User%20Guide/User%20Guide/安装部署教程.md)

## 为什么要开发AutoLine

1. 为中小企业提供一个好用的自动化测试解决方案

2. 为广大软件测试从业人员提供一个基于开源框架的自动化测试平台开发示例

3. 业余写写，练习下敲代码的速度

## 特色

1. 支持Mac、Linux、windows平台

2. 支持Chrome、IE、Edge、Firefox、Safari、HtmlUnitDriver、PhantomJS、Appium、Requests HTTP

3. 支持与selenium-grid集成做分布式测试

等等

## 采用了哪些开源技术/框架

1. Python3

2. Flask

3. EasyUI

4. Chartjs

5. Robotframework

6. Requests

7. SQLAlchemy

8. Appium-Python-Client

9. Selenium3

等等其他及上述技术相关的插件或技术包

## Mysql安装与配置

先安装mysql数据库，使用utf-8字符编码新增autoline数据库

修改.env中关于数据库的配置，主要是：

```
DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1/autoline
TRIGGER_DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1/autoline
```

把上述两个配置中root:12345改为你的mysql的账户和密码
把127.0.0.1改为你的mysql的服务器地址即可

## AutoLine下载及安装依赖

下载AutoLine工程, 在AutoLine根目录下有requirements.txt文件，该文件包含了所有依赖的包，安装好Python3并确保Python3的pip可用，使用以下命令安装AutoLinie依赖库

> pip install -r requirements.txt

等待安装完成

## 配置文件说明
在AutoLine目录下的.env为所有关键的配置项

```INI
# 用于定义运行环境
# production - 生产环境
# development - 开发环境 
AUTOBEAT_CONFIG=production

# 服务器端启动秘钥，这里随意输入一串字符
SECRET_KEY=FJWEOIO138989340SNNFISLDNFIOWFNSNALFKNSDLKF

# SMTP账号
MAIL_SERVER=
MAIL_PORT=587
MAIL_USERNAME=
MAIL_PASSWORD=25
FLASKY_MAIL_SUBJECT_PREFIX=[AutoLine]
FLASKY_MAIL_SENDER=AutoLine Admin <autoline@126.com>

# 默认admin账号, 默认密码123456
FLASKY_ADMIN=autoline@126.com

# 数据库连接字符串
DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1/autoline

# 调度连接字符串
TRIGGER_DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1/autoline
```

## 初始化及运行

在配置好上述配置后如何运行AutoLine？

一. 初始化数据库

> python manage.py db init

> python manage.py db migrate

> python manage.py db upgrade

二. 初始化数据

> python manage.py deploy

三. 内网运行方式

> python manage.py runserver

打开浏览器访问：http://127.0.0.1:5000即可

## 外网访问运行方式

使用下面的命令即可

> python manage.py runserver -h 0.0.0.0 -p 8000

-h 指定ip（ip指定为0.0.0.0即可自定绑定本机IP）    

-p 指定端口号

这时你就可以用在其他机器通过： http://ip:端口     来访问平台了

![首页](./app/static/images/demo/index.png)

使用默认账号： autoline@126.com/123456 登录如图：

![start](./app/static/images/demo/start.png)  

## 如何支持不同的浏览器

下载最新的各浏览器对应的最新驱动，放在bin目录下即可

firefox驱动：https://github.com/mozilla/geckodriver/releases

chrome驱动：https://chromedriver.storage.googleapis.com/index.html

Microsofe Edge驱动：https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

Safari驱动：https://webkit.org/blog/6900/webdriver-support-in-safari-10/

PhantomJS驱动：http://phantomjs.org/releases.html

HtmlUnit驱动：https://sourceforge.net/projects/htmlunit/files/htmlunit/

## 截图
调试模式
![调试模式](./app/static/images/demo/debug_mode.png)

产品管理
![产品管理](./app/static/images/demo/product.png)

项目管理
![项目管理](./app/static/images/demo/project.png)

调度管理
![调度管理](./app/static/images/demo/scheduler_manage.png)


运行日志
![查看任务](./app/static/images/demo/run_logs.png)
![查看任务](./app/static/images/demo/run_logs_detail.png)

查看任务
![查看任务](./app/static/images/demo/task.png)

测试报告
![查看报告](./app/static/images/demo/run_logs_detail.png)

关键字帮助文档
![帮助手册](./app/static/images/demo/help.png)

## 支持与联系

公众号：开源优测  

email：lymking#foxmail.com    

知识星球：开源优测  

关于开源测试技术相关文章首发公众号。

## 许可

AutoLine基于Apache License 2.0协议发布

## 公众号

扫一扫关注我的公众号，获取第一手文档资料：

![开源优测](./app/static/images/deeptest.jpg)
