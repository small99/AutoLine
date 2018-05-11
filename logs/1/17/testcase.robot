*** Settings ***
Library	Collections
Library	DateTime
Library	Dialogs
Library	OperatingSystem
Library	Process
Library	Screenshot
Library	String
Library	Telnet
Library	XML
Library	SeleniumLibrary
Library	AppiumLibrary
Library	RequestsLibrary

Resource	resource.txt

Suite Setup  Screenshot.Set Screenshot Directory	/Users/lyy/Documents/projects/AutoLine/logs/1/17/images

Suite Teardown  SeleniumLibrary.Close all browsers

*** Test Cases ***

1-1 环境初始化.初始化selenium及浏览器环境
	SeleniumLibrary.Open Browser	${url}	${browser}		
	SeleniumLibrary.Maximize Browser Window				
	SeleniumLibrary.Set Selenium Speed	${delay}			


2-2 百度搜索套件.百度搜索测试
	SeleniumLibrary.Go To	${url}			
	SeleniumLibrary.Input Text	${search_input}	${search_word}		
	SeleniumLibrary.Click Button	${search_btn}			
	Screenshot.Take Screenshot				


3-3 清理环境.清理测试环境
	SeleniumLibrary.Close Browser				


