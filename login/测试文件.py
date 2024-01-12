# coding: utf-8

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt


class Example(QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 300)
        self.show()
        self.setWindowTitle('Event handle')

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

