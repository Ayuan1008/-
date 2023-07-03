import pymysql


def select(request, username, password):
    username=request.GET.get("username")
    password=request.GET.get("password")

    conn = pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="root",
        database="train",
        charset="utf8")
    cursor = conn.cursor()
    sql = "select * from user where start='{}' and end='{}' ".format(username, password)
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result