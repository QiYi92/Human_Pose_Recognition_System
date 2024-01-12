from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMenu, QAction, QWidget, QPushButton,QLabel
from main_win.mainwindow import Ui_MainWindow
from main_win.Log_box import Ui_Dialog
from PyQt5.QtCore import Qt, QPoint, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter, QIcon
from PyQt5.Qt import *
from PyQt5 import QtCore, QtWidgets
from concurrent.futures import ThreadPoolExecutor
import pymysql
import sys
import os
import json
import numpy as np
import torch
import torch.backends.cudnn as cudnn

import os
import datetime
import time
import cv2
import detect_openpose
import mysql_connect
# from utils.datasets import LoadImages, LoadWebcam
# from utils.CustomMessageBox import MessageBox
# # LoadWebcam 的最后一个返回值改为 self.cap
# from utils.general import check_img_size, check_requirements, check_imshow, colorstr, non_max_suppression, \
#     apply_classifier, scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path, save_one_box
# from utils.plots import colors, plot_one_box, plot_one_box_PIL
from utils.capnums import Camera
# from dialog.rtsp_win import Window

class RealDet(QObject):
    sendPicture = pyqtSignal(QImage)
    def __init__(self, parent=None):
        super(RealDet, self).__init__(parent)
        self.m_stopFlag = False

    def set_source(self, n):
        self.sourceflag = n

    def set_video_path(self,path):
        self.video_path = path

    def open_camera(self):
        print("in open_camera")
        if(self.sourceflag==0):
            self.cap = cv2.VideoCapture(0)
        else:
            self.cap =cv2.VideoCapture(self.video_path)
        # 利用新的线程开启视频流
        th1 = ThreadPoolExecutor(1)
        th1.submit(self.startDet)


    def close_camera(self):
        self.m_stopFlag = True
        self.cap.release()

    def startDet(self):
        alarms = []
        while not self.m_stopFlag:
            # 判断摔倒标识位
            self.flag_trip = True

            # 读取视频流
            ret, img = self.cap.read()
            if not ret:
                break

            # 目标检测
            p_result = detect_openpose.detect(img)
            print(p_result)
            # self.show_image(img,self.label_real)
            #cv2.imshow("detect-result", img)

            height, width, channel = img.shape
            bytesPerLine = 3 * width
            qt_format = QImage.Format_RGB888 if channel == 3 else QImage.Format_ARGB32

            showImage = QImage(img.data, width, height, bytesPerLine, qt_format)
            if channel == 3:
                showImage = showImage.rgbSwapped()

            else:
                showImage = showImage.convertToFormat(QImage.Format_RGB888)
            # showImage = QImage(img.data, img.shape[1], img.shape[0],
            #                    QImage.Format_RGB888).rgbSwapped()

            self.sendPicture.emit(showImage)
            # 如果结果个数大于10，则清空以前结果
            if (len(alarms) > 10):
                alarms = []
        stopImg = QImage("test1.png")
        self.sendPicture.emit(stopImg)

class add_data(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加数据")

        # 创建布局和控件
        layout = QVBoxLayout(self)
        hlayout_1 = QHBoxLayout(self)
        label = QLabel("记录ID:")
        self.lineEdit = QLineEdit()
        hlayout_1.addWidget(label)
        hlayout_1.addWidget(self.lineEdit)

        hlayout_2 = QHBoxLayout(self)
        label_2 = QLabel("摄像机ID:")  # 创建标签
        self.lineEdit_2 = QLineEdit()  # 创建文本框
        hlayout_2.addWidget(label_2)  # 将标签添加到布局中
        hlayout_2.addWidget(self.lineEdit_2)  # 将文本框添加到布局中

        hlayout_3 = QHBoxLayout(self)
        label_3 = QLabel("检测姿态:")
        self.comboBox_3 = QComboBox()
        self.comboBox_3.addItems(["fall_1", "fall_2"])
        hlayout_3.addWidget(label_3)
        hlayout_3.addWidget(self.comboBox_3)

        hlayout_4 = QHBoxLayout(self)
        button = QPushButton("OK")
        button_cancel = QPushButton("cancel")
        hlayout_4.addWidget(button)
        hlayout_4.addWidget(button_cancel)

        # 将 QLineEdit 与 accept 按钮连接起来
        button.clicked.connect(self.accept)
        button_cancel.clicked.connect(self.reject)

        # 添加控件到布局
        layout.addLayout(hlayout_1)
        layout.addLayout(hlayout_2)
        layout.addLayout(hlayout_3)
        layout.addLayout(hlayout_4)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.m_flag = False
        self.m_stopFlag = False
        self.proPath = "./"
        self.modelPath = "./"
        self.detPath = "./"
        self.flag_trip = True
        self.m_img = QImage()

        # 自动搜索模型
        # 获取训练模型列表
        self.pt_list = os.listdir('./train_model')
        # 筛选出以.pth结尾的文件
        self.pt_list = [file for file in self.pt_list if file.endswith('.pth')]
        # 按文件大小排序
        self.pt_list.sort(key=lambda x: os.path.getsize('./train_model/'+x))
        # 清空下拉框
        self.comboBox.clear()
        self.comboBox_2.clear()
        self.comboBox_3.clear()
        # 将训练模型添加到下拉框中
        self.comboBox.addItems(self.pt_list)
        self.comboBox_2.addItems(self.pt_list)
        self.comboBox_3.addItems(self.pt_list)

        # 状态栏时间显示
        self.statusShowTime()


        #开启定时器刷新
        # self.qtimer_search = QTimer(self)
        # self.qtimer_search.timeout.connect(lambda: self.search_pt())
        # self.qtimer_search.start(2000)
        #定义Action
        self.actionSource.triggered.connect(self.open_file)
        self.actionLibs.triggered.connect(self.open_models)
        self.actionLog.triggered.connect(self.open_log)
        self.actionExit.triggered.connect(self.close)
        #定义按钮
        self.btnReal.clicked.connect(self.real_widget)
        self.btnVideo.clicked.connect(self.video_widget)
        self.btnImg.clicked.connect(self.img_widget)
        self.btnLog.clicked.connect(self.log_widget)
        #界面1
        self.btnStartReal.clicked.connect(self.chose_cam)
        self.btnStopReal.clicked.connect(self.stop)
        #界面2
        self.btnStartVideo.clicked.connect(self.chose_cam)
        self.btnStopVideo.clicked.connect(self.stop)
        #界面3
        self.btnSource.clicked.connect(self.open_file)
        self.btnDir.clicked.connect(self.open_dir)
        self.btnStart.clicked.connect(self.run_img)
        self.btnStop.clicked.connect(self.stop)
        #界面4
        self.btnAdd.clicked.connect(self.on_add)
        self.btnDel.clicked.connect(self.on_del)
        self.btnUpdate.clicked.connect(self.on_update)
        self.btnSelect.clicked.connect(self.on_select)

        self.stackedWidget.setCurrentIndex(0)


        dir = QDir("./video")
        dir.setNameFilters(["*.mp4", "*.avi"])
        list = dir.entryList()
        for i in list:
            self.comboBox_4.addItem(i)

        #self.comboBox.currentTextChanged.connect(self.change_model)
        # self.comboBox.currentTextChanged.connect(lambda x: self.statistic_msg('模型切换为%s' % x))
        # 表头
        self.tableWidget.setHorizontalHeaderLabels(['id', "time", "camera_id", "inspection"])

       # self.load_setting()
    def update_data(self,row, column):
        # 获取更改后的数据
        new_data = self.tableWidget.item(row, column).text()

        # 获取 ID 和要更新的列名
        id = self.tableWidget.item(row, 0).text()
        #column_name = self.tableWidget.horizontalHeaderItem(column).text()

        # 连接数据库
        con = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='openpose_data',
            charset='utf8')
        # 创建游标
        cur = con.cursor()
        #sql = "UPDATE data SET {column_name}=? WHERE id=?" % (new_data, id)

        if column == 0:
            sql = "UPDATE data SET id='%s' WHERE id='%s'" % (new_data, id)
        if column == 1:
            sql = "UPDATE data SET time='%s' WHERE id='%s'" % (new_data, id)
        if column == 2:
            sql = "UPDATE data SET camera_id='%s' WHERE id='%s'" % (new_data, id)
        if column == 3:
            sql = "UPDATE data SET inspection='%s' WHERE id='%s'" % (new_data, id)
        # 获取结果
        try:
            cur.execute(sql)
            con.commit()
        except Exception as e:
            QMessageBox.critical(None, '错误', "更新失败", QMessageBox.Ok)
            con.rollback()
            cur.close()
            con.close()
            return

        # 关闭游标
        cur.close()
        # 关闭数据库连接，目的为了释放内存
        cur.close()

    def on_add(self):
        # 创建并显示 QDialog
        dialog = add_data(self)
        if dialog.exec_() == QDialog.Accepted:
            # 获取 QLineEdit 中的文本
            id = dialog.lineEdit.text()
            camera_id = dialog.lineEdit_2.text()
            inspection = dialog.comboBox_3.currentText()
        else:
            dialog.close()
            return

        # 连接数据库
        con = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='openpose_data',
            charset='utf8')
        # 创建游标
        cur = con.cursor()
        # 生成数据库
        sql_add = "insert into data(id,time,camera_id,inspection) values('%s','%s','%s','%s')" % (id, QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss:zzzz"), camera_id, inspection)
        values = ('0', QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss:zzzz"), '1', 'fall')
        try:
            cur.execute(sql_add)
            con.commit()
        except Exception as e:
            QMessageBox.critical(None, '错误', "添加数据失败", QMessageBox.Ok)
            con.rollback()
            cur.close()
            con.close()
            return
        # 生成数据库
        sql = 'select * from data'
        # 获取结果
        try:
            cur.execute(sql)
            # 获取所有记录  fetchall--获取所有记录   fetchmany--获取多条记录，需传参  fetchone--获取一条记录
            all = cur.fetchall()
        except Exception as e:
            QMessageBox.critical(None, '错误', "查询失败", QMessageBox.Ok)
            con.rollback()
            cur.close()
            con.close()
            return
        # 输出查询结果
        print(all)
        # 关闭游标
        cur.close()
        # 关闭数据库连接，目的为了释放内存
        con.close()
        self.tableWidget.setRowCount(0)
        # 4. 将新行插入到表格中
        row_count = len(all)
        self.tableWidget.setRowCount(row_count)
        for row_number, row_data in enumerate(all):
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                self.tableWidget.setItem(row_number, column_number, item)
        text = "数据新增成功!\n"
        self.textEdit_2.append(text)

    def on_del(self):
        # 连接数据库
        con = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='openpose_data',
            charset='utf8')
        # 创建游标
        cur = con.cursor()
        str=self.tableWidget.selectedItems()[0].text()

        # 生成数据库
        sql = "delete from data where id="+str

        # 获取结果
        try:
            cur.execute(sql)
            con.commit()
        except Exception as e:
            QMessageBox.critical(None, '错误', "删除失败", QMessageBox.Ok)
            con.rollback()
            cur.close()
            con.close()
            return

        # 生成数据库
        sql = 'select * from data'
        try:
            # 获取结果
            cur.execute(sql)
            # 获取所有记录  fetchall--获取所有记录   fetchmany--获取多条记录，需传参  fetchone--获取一条记录
            all = cur.fetchall()
        except Exception as e:
            QMessageBox.critical(None, '错误', "查询失败", QMessageBox.Ok)
            con.rollback()
            cur.close()
            con.close()
            return

        row = cur.rowcount  # 取得记录个数，用于设置表格的行数
        vol = len(all[0])  # 取得字段数，用于设置表格的列数
        # 关闭游标
        cur.close()
        # 关闭数据库连接，目的为了释放内存
        con.close()
        self.tableWidget.setRowCount(0)
        # 4. 将新行插入到表格中
        row_count = len(all)
        self.tableWidget.setRowCount(row_count)
        for row_number, row_data in enumerate(all):
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                self.tableWidget.setItem(row_number, column_number, item)
        text = "数据删除成功!\n"
        self.textEdit_2.append(text)

    def on_update(self):
        # 连接数据库
        con = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='openpose_data',
            charset='utf8')
        # 创建游标
        cur = con.cursor()
        #str = self.lineEdit.text()
        # 生成数据库
        # id = self.tableWidget.selectedItems()[0].text()
        # time = "a"
        # camera_id = "ss"
        # inspection = self.lineEdit.text()
        # sql = "UPDATE data SET id='%s', time='%s', camera_id='%s', inspection='%s' WHERE id='%s'" % (id, time, camera_id, inspection, id)
        #
        # # 获取结果
        # cur.execute(sql)
        # con.commit()
        # 生成数据库
        sql = 'select * from data'
        # 获取结果
        try:
            cur.execute(sql)
            # 获取所有记录  fetchall--获取所有记录   fetchmany--获取多条记录，需传参  fetchone--获取一条记录
            all = cur.fetchall()
        except Exception as e:
            QMessageBox.critical(None, '错误', "查询失败", QMessageBox.Ok)
            con.rollback()
            cur.close()
            con.close()
            return
        # 输出查询结果
        print(all)
        row = cur.rowcount  # 取得记录个数，用于设置表格的行数
        vol = len(all[0])  # 取得字段数，用于设置表格的列数
        # 关闭游标
        cur.close()
        # 关闭数据库连接，目的为了释放内存
        con.close()
        self.tableWidget.setRowCount(0)
        # 4. 将新行插入到表格中
        row_count = len(all)
        self.tableWidget.setRowCount(row_count)
        for row_number, row_data in enumerate(all):
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                self.tableWidget.setItem(row_number, column_number, item)
        text = "数据表更新成功!\n"
        self.textEdit_2.append(text)

    def on_select(self):
        # 连接数据库
        con = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='openpose_data',
            charset='utf8')
        # 创建游标
        cur = con.cursor()
        str = self.lineEdit_2.text()
        # 生成数据库
        sql = "SELECT * FROM data WHERE id LIKE '%{0}%' OR time LIKE '%{0}%' OR camera_id LIKE '%{0}%' OR inspection LIKE '%{0}%'".format(str)
        # 获取结果
        try:
            cur.execute(sql)
            # 获取所有记录  fetchall--获取所有记录   fetchmany--获取多条记录，需传参  fetchone--获取一条记录
            all = cur.fetchall()

            # 输出查询结果
            print(all)
            row = cur.rowcount  # 取得记录个数，用于设置表格的行数
            vol = len(all[0])  # 取得字段数，用于设置表格的列数
            # 关闭游标
            cur.close()
            # 关闭数据库连接，目的为了释放内存
            cur.close()
            self.tableWidget.setRowCount(0)
            # 4. 将新行插入到表格中
            row_count = len(all)
            self.tableWidget.setRowCount(row_count)
            for row_number, row_data in enumerate(all):
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(data)
                    self.tableWidget.setItem(row_number, column_number, item)
            text = "数据检索成功!\n"
            self.textEdit_2.append(text)
        except Exception as e:
            QMessageBox.critical(None, '错误', "输入正确的id", QMessageBox.Ok)
            text1 = "数据检索失败!\n"
            self.textEdit_2.append(text1)

    def open_file(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile('./data'))

    def open_models(self):
        self.modelPath = QFileDialog.getExistingDirectory(self, "Select Model Floder", "",)
        if self.modelPath:
            self.label_2.setText(self.modelPath)

    def open_log(self):

        self.stackedWidget.setCurrentIndex(2)

    def real_widget(self):
        self.stackedWidget.setCurrentIndex(0)

    def video_widget(self):
        self.stackedWidget.setCurrentIndex(1)

    def img_widget(self):
        self.stackedWidget.setCurrentIndex(2)

    def log_widget(self):
        self.stackedWidget.setCurrentIndex(3)
        # 连接数据库
        con = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='openpose_data',
            charset='utf8')
        # # 创建游标
        cur = con.cursor()
        # 生成数据库
        sql = 'select * from data'
        # 获取结果
        cur.execute(sql)
        # 获取所有记录  fetchall--获取所有记录   fetchmany--获取多条记录，需传参  fetchone--获取一条记录
        all = cur.fetchall()

        row = cur.rowcount  # 取得记录个数，用于设置表格的行数
        vol = len(all[0])  # 取得字段数，用于设置表格的列数
        # 关闭游标
        cur.close()
        # 关闭数据库连接，目的为了释放内存
        con.close()
        # self.tableWidget.clear()
        self.tableWidget.setRowCount(row)
        self.tableWidget.setColumnCount(vol)

        for i in range(row):
            for j in range(vol):
                temp_data = all[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.tableWidget.setItem(i, j, data)
        self.tableWidget.cellChanged.connect(self.update_data)

    def statusShowTime(self):
        self.timeLabel = QLabel()  # 设置一个label的控件
        self.statusBar.addPermanentWidget(self.timeLabel, 0)  # 将label控件放进状态栏
        self.Timer = QTimer()  # 自定义QTimer类
        self.Timer.start(1000)  # 每1s运行一次
        self.Timer.timeout.connect(self.updateTime)  # 与updateTime函数连接

    def updateTime(self):
        time = QDateTime.currentDateTime()  # 获取现在的时间
        timeplay = time.toString('yyyy-MM-dd hh:mm:ss dddd')  # 设置显示时间的格式
        self.timeLabel.setText(timeplay)  # 设置timeLabel控件显示的内容

    def run_real(self):
        self.chose_cam(self)

    def run_img(self):
        # 测试文件夹路径
        path = self.proPath + "/data"
        # 结果保存路径
        save_path = path + "_result"
        print(save_path)
        # 如果结果保存路径不存在，则创建
        if not os.path.exists(save_path):
            os.mkdir(save_path)

        # 获取文件夹中的所有文件
        files = []
        for root, dirs, files in os.walk(path, topdown=True):
            imgs = files

        # 初始化计数器
        num = 0
        # 遍历文件夹中的所有文件
        for file in files:
            if (self.m_stopFlag == True):
                break
            # 读取图像
            img = cv2.imread(path + "\\" + file)
            # 进行目标检测
            start_time = time.time()    # 程序开始时间
            detect_openpose.detect(img)
            p_result = detect_openpose.detect(img)
            end_time = time.time()      # 程序结束时间
            run_time = end_time - start_time    # 程序的运行时间，单位为秒

            # 保存结果图像
            name = save_path + "\\res" + file
            cv2.imwrite(name, img)
            num += 1
            print("检测第 ", str(num), " 图像!")
            text = "检测第 "+str(num)+" 图像!\n"
            print(p_result)
            text2 = str(p_result)+"\n"
            print("运行时间为：", str('%.2f' % run_time))
            text1 = "运行时间为："+str('%.2f' % run_time)+"秒！\n"
            self.textEdit.append(text)  # labelruning可以是文本部件或标签部件
            self.textEdit.append(text1)
            self.textEdit.append(text2)





    def open_dir(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile('./data_result'))

    def search_pt(self):
        pt_list = os.listdir('./train_model')
        pt_list = [file for file in pt_list if file.endswith('.pth')]
        pt_list.sort(key=lambda x: os.path.getsize('./train_model/' + x))

        if pt_list != self.pt_list:
            self.pt_list = pt_list
            self.comboBox.clear()
            self.comboBox.addItems(self.pt_list)

    def chose_cam(self):
        # 检测线程
        self.camera_thread = RealDet()
        # 连接Camera的sendPicture信号与receive函数进行展示
        self.camera_thread.sendPicture[QImage].connect(self.on_showImage)
        if(self.stackedWidget.currentIndex() == 0):
            self.camera_thread.set_source(0)
        if(self.stackedWidget.currentIndex() == 1):
            self.camera_thread.set_source(1)
            self.camera_thread.set_video_path("./video/" + self.comboBox_4.currentText())

        self.camera_thread.open_camera()

    def show_msg(self, msg):
        self.runButton.setChecked(Qt.Unchecked)
        self.statistic_msg(msg)
        if msg == "检测结束":
            self.saveCheckBox.setEnabled(True)

    def change_model(self, x):
        self.model_type = self.comboBox.currentText()
        self.det_thread.weights = "./pt/%s" % self.model_type
        self.statistic_msg('模型切换为%s' % x)

    # 退出检测循环
    def stop(self):
        if(self.stackedWidget.currentIndex() == 2):
            self.m_stopFlag = True
        else:
            self.camera_thread.close_camera()

    def on_showImage(self,img):
        if(self.stackedWidget.currentIndex() == 0):
            img_height = self.label_real.height()
            img_width = self.label_real.width()
            new_img = img.scaled(QSize(img_width, img_height))
            self.label_real.setPixmap(QPixmap.fromImage(new_img))
        if (self.stackedWidget.currentIndex() == 1):
            img_height = self.label_6.height()
            img_width = self.label_6.width()
            new_img = img.scaled(QSize(img_width, img_height))
            self.label_6.setPixmap(QPixmap.fromImage(new_img))

    # 实时统计
    def show_statistic(self, statistic_dic):
        try:
            self.resultWidget.clear()
            statistic_dic = sorted(statistic_dic.items(), key=lambda x: x[1], reverse=True)
            statistic_dic = [i for i in statistic_dic if i[1] > 0]
            results = [' '+str(i[0]) + '：' + str(i[1]) for i in statistic_dic]
            self.resultWidget.addItems(results)

        except Exception as e:
            print(repr(e))

    def closeEvent(self, event):
        # 如果摄像头开着，先把摄像头关了再退出，否则极大可能可能导致检测线程未退出
        # self.det_thread.jump_out = True
        sys.exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MainWindow()
    myWin.show()
    sys.exit(app.exec_())
