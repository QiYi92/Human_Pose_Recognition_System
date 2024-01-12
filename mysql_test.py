import sys #这句可能是不需要的
from PyQt5 import QtSql
# import ctypes
if __name__ == '__main__':
    # ctypes.windll.LoadLibrary('C:/mysql/mysql8028/lib/libmysql.dll') #如果不想把libmysql.dll文件从mysql安装目录复制到PyQt的bin目录下，那就加上这一句，也能解决问题。
    db = QtSql.QSqlDatabase.addDatabase("QMYSQL")
    db.setHostName("localhost")
    db.setDatabaseName("openpose_data") #自己的数据库名字
    db.setUserName("root")
    db.setPassword("root")
    db.setPort(3306)
    print(db.open())
    print(QtSql.QSqlDatabase.drivers())
    print(db.lastError().text())
