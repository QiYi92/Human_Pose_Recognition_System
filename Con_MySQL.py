from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import ctypes
from sys import _getframe
from builtins import print as _print

def print(*arg, **kw):
    s = f'路径:{_getframe(1).f_code.co_filename}...函数{_getframe(1).f_code.co_name}的{_getframe(1).f_lineno} 行：'  # 注此处需加参数 1。
    return _print(s, *arg, **kw)


class Oper_Mysql():
    global db
    def __init__(self):
        super(Oper_Mysql, self).__init__()
        print(QSqlDatabase.drivers())  #打印支持驱动
        # 加载MySQL驱动
        ctypes.windll.LoadLibrary('C:/Program Files/MySQL/MySQL Server 8.0/lib/libmysql.dll')  # 根本原因是qt用的是c++的库，加载不到驱动。用python 加载dll 让python 在上下文中能读取到驱动
        # 添加数据库
        db = QSqlDatabase.addDatabase('QMYSQL')
        # 设置主机名和端口号
        db.setHostName('localhost')
        db.setPort(3306)
        # 设置数据库名、用户名和密码
        db.setDatabaseName('openpose_data')
        db.setUserName('root')
        db.setPassword('root')
        # 打开数据库
        if db.open():
            print("数据库连接成功")
        else:
            print("数据库连接失败")


    # 对数据库增删改查
    def ZSGC_Mysql(self):
        #创建注册用户表 并设置主键
        query = QSqlQuery()
        e = query.exec_("create table if not exists Environment("
                        "E_ID int not null primary key auto_increment, E_Time datetime, E_Temp float, E_Hum float, E_Pre float, E_Oxy float, "
                        "E_Wind float, E_Smog float)")
        m = query.exec_("create table if not exists Management(M_UserID int not null primary key, M_UserName varchar(255), M_PassWord varchar(255), M_UserRole varchar(255))")
        t = query.exec_("create table if not exists ThresholdWarning(TW_Id int not null primary key auto_increment, TW_E_Temp float,"
                        " TW_E_Hum float, TW_E_Pre float, TW_E_Oxy float, TW_E_Wind float, TW_E_Smog float)")
        w = query.exec_("create table if not exists Warning(W_WarningID int not null primary key auto_increment, W_Time datetime, W_Signal varchar(255), W_Type  varchar(255))")
        f = query.exec_("create table if not exists Forewarning(FW_WarningID int not null primary key auto_increment, FW_Time datetime, FW_Signal varchar(255), "
                        "FE_Level int, FW_LevelName varchar(255))")
        a = query.exec_("create table if not exists AccidentInfo(Ac_Time datetime not null primary key, Ac_Address varchar(255), Ac_Type varchar(255), Ac_Mange varchar(255))")
        h = query.exec_("create table if not exists WareHouse(H_ID int not null primary key auto_increment, H_Name varchar(255), H_Site varchar(255),"
                        "H_length double, H_width double, H_height double)")

        if e and m and t and w and f and a and h:
            print("数据表载入成功")

if __name__=="__main__":
    aa= Oper_Mysql()
    aa.ZSGC_Mysql()





