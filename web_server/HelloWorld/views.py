import datetime
import json
import sys
import time
# from datetime import datetime

import requests
from django.http import HttpResponse
import pymysql

from bs4 import BeautifulSoup
from flask import request
from lxml import etree

kv = {"user-agent": "Mozilla/5.0"}
parser = etree.HTMLParser(encoding='utf-8')


def getPaeg(url):
    try:
        r = requests.get(url, timeout=30, headers=kv)
        r.raise_for_status()  # 如果状态码不是200，将产生一次异常
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "产生异常"


def getmessag(request):
    start = request.GET.get("fromCn")
    end = request.GET.get("toCn")
    time = request.GET.get("fromDate")

    url = "https://www.suanya.com/pages/trainList?fromCn=" + start + "&toCn=" + end + "&fromDate=" + time
    newtotals = []
    newends = []
    content = getPaeg(url)
    parser = etree.HTMLParser(encoding="utf-8")
    html = etree.HTML(content, parser=parser)
    trainnames = html.xpath(
        "//div[@class='lisBox']/div/div[@class='tbody']/div[@class='railway_list']/div[@class='w1']/div/strong/text()")
    totaltimes = html.xpath(
        "//div[@class='lisBox']/div/div[@class='tbody']/div[@class='railway_list']/div[@class='w4']/div/text()")

    starttimes = html.xpath(
        "//div[@class='lisBox']/div/div[@class='tbody']/div[@class='railway_list']/div[@class='w2']/div/strong/text()")
    endtimes = html.xpath(
        "//div[@class='lisBox']/div/div[@class='tbody']/div[@class='railway_list']/div[@class='w2']/div[2]/label/text()")
    typeonemoney = html.xpath("//*[@id='train-list']/div[4]/div[1]/div[6]/div/div/div[1]/div[5]/div[1]/b/text()")
    typetwomoney = html.xpath(
        "//div[@class='lisBox']/div/div[@class='tbody']/div[@class='railway_list']/div[@class='w5']/div[2]/b/text()")
    typethreemoney = html.xpath("//*[@id='train-list']/div[4]/div[1]/div[6]/div/div/div[1]/div[5]/div[3]/b/text()")

    typeone = html.xpath("//*[@id='train-list']/div[4]/div[1]/div[6]/div/div/div[1]/div[5]/div[1]/span/text()")
    typetwo = html.xpath("//*[@id='train-list']/div[4]/div[1]/div[6]/div/div/div[1]/div[5]/div[2]/span/text()")
    typethree = html.xpath("//*[@id='train-list']/div[4]/div[1]/div[6]/div/div/div[1]/div[5]/div[3]/span/text()")
    startstation = html.xpath("//*[@id='train-list']/div[4]/div[1]/div[6]/div/div/div[1]/div[3]/div[1]/span/text()")
    endstation = html.xpath("//*[@id='train-list']/div[4]/div[1]/div[6]/div/div/div[1]/div[3]/div[2]/span/text()")
    for item in totaltimes:
        newtotals.append(str(item).replace(" ", "").strip())

    for item in endtimes:
        newends.append(str(item).replace(" ", "").strip())

    trains = []


    for i in range(0, len(trainnames)):
        train = {}
        train["trainName"] = trainnames[i]
        train["startTime"] = starttimes[i]
        train["endTime"] = newends[i]
        train["allTime"] = newtotals[i].replace("时", "h").replace("分", "m")

        train[typeone[i]] = typeonemoney[i]
        train[typetwo[i]] = typetwomoney[i]
        train[typethree[i]] = typethreemoney[i]
        train["startstation"] = startstation[i]
        train["endstation"] = endstation[i]
        trains.append(train)
    result = json.dumps(trains, ensure_ascii=False)
    return HttpResponse(result)


def searchhistory(request):
    start = request.GET.get("fromCn")
    end = request.GET.get("toCn")
    time = request.GET.get("fromDate")
    username = request.GET.get("username")
    conn = getconnect()
    cursor = conn.cursor()

    # searchtime = time.strftime("%y-%m-%d %h:%m:%s", time.localtime())

    dt = datetime.datetime.now()
    searchtime = dt.strftime("%Y-%m-%d %H:%M:%S")
    #     先通过username查到user的id
    sql = "select id from user where username='{}'".format(username)
    try:
        cursor.execute(sql)
        res = cursor.fetchall()
        uid = res[0][0]
    except:
        return HttpResponse(None)
    #     插入一条查询记录
    sql = "insert into searchhistory (uid,start,end,searchtime,traintime) values ('{}','{}','{}','{}','{}')".format(uid,
                                                                                                                    start,
                                                                                                                    end,
                                                                                                                    searchtime,
                                                                                                                    time)
    try:
        flag = cursor.execute(sql)
        conn.commit()
    except:
        return HttpResponse(None)
    if flag > 0:
        tip = "searchhistory add success"
        cursor.close()
        conn.close()
        return getjson(tip)
    else:
        tip = "searchhistory add fail"
        cursor.close()
        conn.close()
        return getjson(tip)


def getconnect():
    conn = pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="root",
        database="train",
        charset="utf8")

    return conn


def getjson(tips):
    result = []
    res = {}
    res['result'] = tips
    result.append(res)
    mes = json.dumps(result)
    return HttpResponse(mes)


def login(request):
    global username
    username = request.GET.get("username")
    password = request.GET.get("password")
    conn = getconnect()
    cursor = conn.cursor()
    try:
        sql = "select username from user where username='{}'".format(username)
        cursor.execute(sql)
        res = cursor.fetchall()
    except:
        return HttpResponse(None)

    if (len(res) == 0):
        tip = "user has not exist"
        cursor.close()
        conn.close()
        return getjson(tip)
    else:
        try:
            sql = "select password from user where username='{}'".format(username)
            cursor.execute(sql)
            res = cursor.fetchall()
            res = str(res[0][0])
            if res == password:
                tip = "login success"

                cursor.close()
                conn.close()
                return getjson(tip)
            else:
                tip = "password error"
                cursor.close()
                conn.close()
                return getjson(tip)
        except():
            return HttpResponse(None)


def register(request):
    username = request.GET.get("username")
    password = request.GET.get("password")
    conn = getconnect()
    cursor = conn.cursor()

    sql = "select username from user where username='{}'".format(username)
    try:
        cursor.execute(sql)
        res = cursor.fetchall()
        if (len(res) != 0):
            tip = "username has exist"
            cursor.close()
            conn.close()
            return getjson(tip)
    except:
        return HttpResponse(None)

    sql = "insert into user (username,password) values ('{}','{}')".format(username, password)
    try:

        flag = cursor.execute(sql)
        conn.commit()
        if flag > 0:
            cursor.close()
            conn.close()
            tip = "add user success"
            return getjson(tip)
        else:
            tip = "add user fail"
            cursor.close()
            conn.close()
            return getjson(tip)
    except:
        conn.rollback()
        return HttpResponse(None)


def updatepassword(request):
    username = request.GET.get("username")
    password = request.GET.get("password")
    conn = getconnect()
    cursor = conn.cursor()

    sql = "update user set password='{}' where username='{}'".format(password, username)
    try:
        flag = cursor.execute(sql)
        conn.commit()
    except:
        return HttpResponse(None)
    if flag > 0:
        tip = "password update success"
        cursor.close()
        conn.close()
        return getjson(tip)
    else:
        tip = "password update fail"
        cursor.close()
        conn.close()
        return getjson(tip)


# def updateuser(request):
#     username = request.GET.get("username")
#     password = request.GET.get("password")
#
#     conn = getconnect()
#     cursor = conn.cursor()
#     # 通过username查到user表的id
#     sql = "select id from user where username='{}'".format(username)
#     try:
#         cursor.execute(sql)
#         uid = cursor.fetchall()
#         uid = str(uid[0][0])
#     except:
#         return HttpResponse(None)
#
#     sql = "update user set username='{}',password='{}' where id='{}'".format(username, password, uid)
#     try:
#         flag = cursor.execute(sql)
#         conn.commit()
#     except:
#         return HttpResponse(None)
#
#     if flag > 0:
#         tip = "user update success"
#         cursor.close()
#         conn.close()
#         return getjson(tip)
#     else:
#         tip = "user update fail"
#         cursor.close()
#         conn.close()
#         return getjson(tip)

def addorder(request):
    username = request.GET.get("username")
    trainname = request.GET.get("trainname")
    trainseat = request.GET.get("trainseat")
    starttime = request.GET.get("starttime")
    endtime = request.GET.get("endtime")
    alltime = request.GET.get("alltime")
    startstation = request.GET.get("startstation")
    endstation = request.GET.get("endstation")

    dt = datetime.datetime.now()
    addtime = dt.strftime("%Y-%m-%d %H:%M:%S")

    conn = getconnect()
    cursor = conn.cursor()

    sql = "insert into `order`(trainname,trainseat,starttime,endtime,alltime,addtime,username,startstation,endstation)  values ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
        trainname,
        trainseat,
        starttime,
        endtime,
        alltime,
        addtime,
        username,
        startstation,
        endstation
    )
    print(sql)
    try:
        flag = cursor.execute(sql)
        conn.commit()
    except:
        return HttpResponse(None)
    if flag > 0:
        tip = "order add success"
        cursor.close()
        conn.close()
        return getjson(tip)
    else:
        tip = "order add fail"
        cursor.close()
        conn.close()
        return getjson(tip)


def searchorder(request):
    results = []
    keys = ["trainname", "trainseat", "starttime", "endtime", "alltime", "addtime", "username", "startstation",
            "endstation"]
    username = request.GET.get("username")
    conn = getconnect()
    cursor = conn.cursor()

    sql = "select trainname,trainseat,starttime,endtime,alltime,addtime,username,startstation,endstation from `order` where username='{}'".format(
        username)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    except:
        return HttpResponse(None)

    if len(result) > 0:
        for items in result:
            res = {}
            for i in range(0,len(keys)):
                res[str(keys[i])]=items[i]
            results.append(res)
        results = json.dumps(results, ensure_ascii=False)

        return HttpResponse(results)
    else:
        tip = "search order fail"
        cursor.close()
        conn.close()
        return getjson(tip)


def usercenter(request):
    age = request.GET.get("age")
    sex = request.GET.get("sex")
    usertype = request.GET.get("usertype")
    email = request.GET.get("email")
    address = request.GET.get("address")

    conn = getconnect()
    cursor = conn.cursor()

    # 通过username查到user表的id
    sql = "select id from user where username='{}'".format(username)
    try:
        cursor.execute(sql)
        uid = cursor.fetchall()
        uid = str(uid[0][0])
    except:
        return HttpResponse(None)

    #     查看个人中心有没有该用户的个人信息，如果没有就插入，如果有就更新
    sql = "select * from usermessage where uid='{}'".format(uid)
    try:
        cursor.execute(sql)
        res = cursor.fetchall()
    except:
        return HttpResponse(None)

    if len(res) > 0:
        #         做更新操作
        sql = "update usermessage set age='{}',sex='{}',usertype='{}',email='{}',address='{}' where uid='{}'".format(
            age, sex, usertype, email, address, uid)
        try:
            flag = cursor.execute(sql)
            conn.commit()
        except:
            return HttpResponse(None)
        if flag > 0:
            tip = "usermessage update success"
            cursor.close()
            conn.close()
            return getjson(tip)
        else:
            tip = "usermessage update fail"
            cursor.close()
            conn.close()
            return getjson(tip)

    else:
        sql = "insert into usermessage (age,sex,usertype,email,address,uid) values ('{}','{}','{}','{}','{}','{}')".format(
            age, sex, usertype, email, address, uid)
        try:
            flag = cursor.execute(sql)
            conn.commit()
        except:
            return HttpResponse(None)
        if flag > 0:
            tip = "usermessage add success"
            cursor.close()
            conn.close()
            return getjson(tip)
        else:
            tip = "usermessage add fail"
            cursor.close()
            conn.close()
            return getjson(tip)
