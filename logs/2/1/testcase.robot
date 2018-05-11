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

Suite Setup  Screenshot.Set Screenshot Directory	/Users/lyy/Documents/projects/AutoLine/logs/2/1/images

Suite Teardown  Close all browsers

*** Test Cases ***

