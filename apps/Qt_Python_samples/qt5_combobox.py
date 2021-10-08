import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setGeometry(200, 200, 300, 300)
        self.setWindowTitle("Qt test window")

        self.first_cb = QtWidgets.QComboBox(self)
        self.first_cb.setGeometry(70, 80, 150, 25)
        self.first_cb.setAccessibleName("Q1")
        self.first_cb.addItems(["Image on left (default)", "Image on right", "Image on top"])

        self.second_cb = QtWidgets.QComboBox(self)
        self.second_cb.setGeometry(70, 130, 150, 25)
        self.second_cb.setAccessibleName("Q2")
        self.second_cb.addItems(["Image", "Text", "Image and Text"])

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
