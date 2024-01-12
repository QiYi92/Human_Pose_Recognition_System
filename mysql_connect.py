import sys #这句可能是不需要的
import ctypes
from PyQt5 import QtSql
#import ctypes
if __name__ == '__main__':
    # ctypes.windll.LoadLibrary('C:/Program Files/MySQL/MySQL Server 8.0/lib/libmysql.dll')
    db = QtSql.QSqlDatabase.addDatabase('QMYSQL')
    db.setHostName('localhost')
    db.setDatabaseName("openpose_data") #自己的数据库名字
    db.setUserName("root")
    db.setPassword("root")
    db.setPort(3306)
    print(db.open())
    print(QtSql.QSqlDatabase.drivers())