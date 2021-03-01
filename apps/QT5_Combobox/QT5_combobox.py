from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

import sys
class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow,self).__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 300, 300)
        self.setWindowTitle("Qt test window")

        self.d1 = QtWidgets.QComboBox(self)
        self.d1.setGeometry(70, 80, 150, 25)
        self.d1.setAccessibleName("Q1")
        self.d1.addItems(["Image on left (default)", "Image on right", "Image on top"])

        self.d2 = QtWidgets.QComboBox(self)
        self.d2.setGeometry(70, 130, 150, 25)
        self.d2.setAccessibleName("Q2")
        self.d2.addItems(["Image", "Text", "Image and Text"])

    def update(self):
        self.label.adjustSize()


def window():
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    win.setAccessibleName("QTRV")
    win.show()

    sys.exit(app.exec_())

window()