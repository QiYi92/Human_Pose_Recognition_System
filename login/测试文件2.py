# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'regist.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QLineEdit, QLabel
from Con_MySQL import *
from PyQt5.QtCore import pyqtSignal



class Regist_Ui(QWidget):
    SuccessReg = pyqtSignal()  # 定义一个信号
    def __init__(self):  #类似于构造函数， self不算参数个数
        super(Regist_Ui, self).__init__()
        self.setupUi(self)
        # self.conMysql()
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(577, 459)
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(70, 70, 421, 291))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Username = QtWidgets.QLabel(self.layoutWidget)
        self.Username.setObjectName("Username")
        self.horizontalLayout.addWidget(self.Username)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.lineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit.setMinimumSize(QtCore.QSize(201, 31))
        self.lineEdit.setMaximumSize(QtCore.QSize(201, 31))
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.Password = QtWidgets.QLabel(self.layoutWidget)
        self.Password.setObjectName("Password")
        self.horizontalLayout_2.addWidget(self.Password)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_2.setMinimumSize(QtCore.QSize(201, 31))
        self.lineEdit_2.setMaximumSize(QtCore.QSize(201, 31))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout_2.addWidget(self.lineEdit_2)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.PasswordSure = QtWidgets.QLabel(self.layoutWidget)
        self.PasswordSure.setObjectName("PasswordSure")
        self.horizontalLayout_3.addWidget(self.PasswordSure)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_3.setMinimumSize(QtCore.QSize(201, 31))
        self.lineEdit_3.setMaximumSize(QtCore.QSize(201, 31))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout_3.addWidget(self.lineEdit_3)
        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.UserType = QtWidgets.QLabel(self.layoutWidget)
        self.UserType.setObjectName("UserType")
        self.horizontalLayout_4.addWidget(self.UserType)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.comboBox = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox.setMinimumSize(QtCore.QSize(201, 31))
        self.comboBox.setMaximumSize(QtCore.QSize(201, 31))
        font = QtGui.QFont()
        font.setFamily("Adobe Arabic")
        font.setPointSize(14)
        self.comboBox.setFont(font)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_4.addWidget(self.comboBox)
        self.gridLayout.addLayout(self.horizontalLayout_4, 3, 0, 1, 1)
        self.layoutWidget1 = QtWidgets.QWidget(Form)
        self.layoutWidget1.setGeometry(QtCore.QRect(140, 380, 271, 51))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.ConfirmButton = QtWidgets.QPushButton(self.layoutWidget1)
        self.ConfirmButton.setMinimumSize(QtCore.QSize(100, 35))
        self.ConfirmButton.setMaximumSize(QtCore.QSize(100, 35))
        font = QtGui.QFont()
        font.setFamily("Adobe Arabic")
        font.setPointSize(16)
        self.ConfirmButton.setFont(font)
        self.ConfirmButton.setObjectName("ConfirmButton")
        self.horizontalLayout_5.addWidget(self.ConfirmButton)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem4)
        self.CancelButton = QtWidgets.QPushButton(self.layoutWidget1)
        self.CancelButton.setMinimumSize(QtCore.QSize(100, 35))
        self.CancelButton.setMaximumSize(QtCore.QSize(100, 35))
        font = QtGui.QFont()
        font.setFamily("Adobe Arabic")
        font.setPointSize(16)
        self.CancelButton.setFont(font)
        self.CancelButton.setObjectName("CancelButton")
        self.horizontalLayout_5.addWidget(self.CancelButton)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "新用户注册"))
        self.Username.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:16pt;\">用户名</span></p></body></html>"))
        self.Password.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:16pt;\">密码</span></p></body></html>"))
        self.PasswordSure.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:16pt;\">确认密码</span></p></body></html>"))
        self.UserType.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:16pt;\">用户类型</span></p></body></html>"))
        self.comboBox.setItemText(0, _translate("Form", "管理员"))
        self.comboBox.setItemText(1, _translate("Form", "仓库主管"))
        self.comboBox.setItemText(2, _translate("Form", "工作人员"))
        self.comboBox.setItemText(3, _translate("Form", None))
        self.ConfirmButton.setText(_translate("Form", "确定"))
        self.CancelButton.setText(_translate("Form", "取消"))

        self.lineEdit.setFocus()  #鼠标焦点
        self.lineEdit.setPlaceholderText("请输入姓名") #提示信息
        self.lineEdit_2.setPlaceholderText("请输入密码")
        self.lineEdit_3.setPlaceholderText("请确认密码")
        self.lineEdit_2.setEchoMode(QLineEdit.Password)  #密码隐藏
        self.lineEdit_3.setEchoMode(QLineEdit.Password)

        self.comboBox.setCurrentIndex(3)  #设置默认值 为空
        self.comboBox.activated.connect(self.emit_identity) #当选中下拉框时发射信号
        self.lineEdit.textChanged.connect(self.emit_Username) #姓名改变时
        self.lineEdit_2.textChanged.connect(self.emit_Password) #密码
        self.lineEdit_3.textChanged.connect(self.emit_ConPassword) #确认密码
        self.ConfirmButton.clicked.connect(self.emit_Confir_Button) #确认
        self.CancelButton.clicked.connect(self.emit_Cancel) #取消

    def emit_Username(self):
        print("UserName发生改变")

    def emit_Password(self):
        print("PassWord发生改变")

    def emit_ConPassword(self):
        print("ConPassword发生改变")

    def emit_identity(self):  #发射身份信号
        self.ident.emit(str(self.comboBox.currentText()))

    def emit_Confir_Button(self):
        if self.lineEdit.text().strip() == '' or self.lineEdit_2.text().strip() == '' or self.lineEdit_3.text().strip() == '':
            try:
                QMessageBox.information(self, "error", "输入有误，请重新输入")
            except Exception as str:
                print("输入错误 %s" %(str))
        elif self.lineEdit_2.text() != self.lineEdit_3.text():
            try:
                QMessageBox.information(self, "error", "两次密码输入不一致")
            except Exception as str:
                print("未知错误 %s" %(str))
        else:
                QMessageBox.information(self, "QAQ", "注册成功")
                UserName=self.lineEdit.text()
                PassWord = self.lineEdit_2.text()
                ConPassWord = self.lineEdit_3.text()

                self.SuccessReg.emit()

    def emit_Cancel(self):
        self.SuccessReg.emit()






if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    w = Regist_Ui()
    w.setupUi(widget)
    widget.show()
    sys.exit(app.exec())
