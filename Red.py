#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import json
import smtplib
import threading
from sys import exit as sys_exit
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from plyer import notification
from traay import *
import time
import traceback
import ast
import datetime

url = "http://www.oref.org.il/WarningMessages/Alert/alerts.json"
url2 = "http://www.oref.org.il/WarningMessages/Alert/alerts.json?v=1"
url3 = "http://www.oref.org.il/WarningMessages/History/AlertsHistory.json"
url4 = "http://www.oref.org.il/1096-he/Pakar.aspx"
NAMES = {}
LONGSTR = ""
my_icon = "Bell_02.ico"
fromaddr = ""
toaddr = ""
password = ""
server = None
ALERT_IDS = []


def get_areas_and_cities():
    global NAMES
    to_search = "var cities ="
    to_search2 = "</script>"
    to_search3 = "var areas ="
    respone = requests.get(url4)
    body = respone.content
    indx1 = body.index(to_search)
    indx2 = body.index(to_search2,indx1)
    cities = body[indx1+13:indx2-4]
    cities = cities.replace("label", '"label"')
    cities = cities.replace("value", '"value"')
    cities = cities.replace("id", '"id"')
    cities = ast.literal_eval(cities)
    indx1 = body.index(to_search3)
    indx2 = body.index(to_search2,indx1)
    areas = body[indx1+12:indx2-4]
    areas = areas.replace("label",'"label"')
    areas = areas.replace("value",'"value"')
    areas = ast.literal_eval(areas)
    areas_by_cities = {}
    cities_by_value = {}
    for city in cities:
        value = city['value']
        label = city['label']
        if value in cities_by_value:
            cities_by_value[value].append(label)
        else:
            cities_by_value[value] = [label]
    for area in areas:
        value = area['value']
        label = area['label']
        if value in cities_by_value:
            areas_by_cities[label] = cities_by_value[value]
        else:
            areas_by_cities[label] = 'שטח פתוח - אין יישובים'

    for i in areas_by_cities:
        print i + "   :" + str(areas_by_cities[i])

    NAMES = areas_by_cities



def tip_noti(Merhav):
    notification.notify(
        title=u"צבע אדום באזור - " + Merhav,
        message=NAMES[Merhav][0],
        app_name="Red Alert",
        timeout=3,
        app_icon=my_icon
    )


def handle_alert(info):
    to_send = ""
    for alert in info:
        try:
            fl = open("log.txt", 'a')
            print "Finally...."
            summit = ""
            d1 = alert['data']
            d2 = alert['title']
            d3 = alert['id']
            if d3 in ALERT_IDS:
                continue
            ALERT_IDS.append(d3)
            names_to_noti = []
            for ezor in d1:
                summit += u"צבע אדום באזור - " + ezor.decode("utf-8") + u" ביישובים הבאים: " + NAMES[ezor.decode('utf-8')][0] + "\r\n" + str(datetime.datetime.now()) + "\r\n"
                names_to_noti.append(ezor)
            fl.write(summit.encode('utf-8'))
            fl.close()
            to_send += summit
            for ezor in names_to_noti:
                t = threading.Thread(target=tip_noti,args=(ezor,))
                t.start()
        except Exception as exx:
            fl.close()
            fl2 = open("error.txt", 'a')
            fl2.write(traceback.format_exc() + "\r\n")
            fl2.close()
    if to_send == "":
        pass
    else:
        send_emaile(to_send.encode('utf-8'))


def bye(trya):
    print "Exiting..."
    sys_exit(1)


def foo(asd):
    pass


def start_tray():
    try:
        hover_text = "Red Alert V1"
        menu_options = ()
        SysTrayIcon(my_icon, hover_text, menu_options, on_quit=bye, default_menu_index=0)
    except Exception as exx:
        fl2 = open("error.txt", 'a')
        fl2.write(traceback.format_exc() + "\r\n")
        fl2.close()


def send_emaile(Body):
    email_login()
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = u"צבע אדום"
    body = Body
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.close()


def email_login():
    global server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, password)


def initialize():
    get_areas_and_cities() #generate dictionary of the areas
    t = threading.Thread(target=start_tray)
    t.start()


def main():
    # tip_noti(u"עמק חפר 139")
    initialize()
    while True:
        try:
            response = requests.get(url2)
            data = response.content
            if '<h1>Not Found</h1>' not in data:
                if len(data) == 3:
                    pass
                else:
                    info = ast.literal_eval(data)
                    info = [info]
                    t = threading.Thread(target=handle_alert, args=(info,))
                    t.start()
                print "Its quiet here....",
                time.sleep(1)
            else:
                time.sleep(10)
                f3 = open("itswierd2.txt", 'a')
                f3.write(data)
                f3.close()
        except requests.exceptions.ConnectionError:
            print "working"
            fl2 = open("error.txt", 'a')
            fl2.write("time: " + str(time.gmtime()) +"\r\n"+traceback.format_exc()+"\r\n")
            fl2.close()
            time.sleep(10)
        except Exception:
            print "yoooooooo"
            fl2 = open("error.txt", 'a')
            fl2.write(traceback.format_exc() + "\r\n")
            fl2.close()


if __name__ == '__main__':
    main()
