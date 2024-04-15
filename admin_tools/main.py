from PyQt5 import QtCore, QtGui, QtWidgets
from AnimationShadowEffect import AnimationShadowEffect                         # !!!

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(307, 158)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

#        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton = PushButton(self.centralwidget)                         # +++

        self.pushButton.setGeometry(QtCore.QRect(70, 50, 171, 51))
        self.pushButton.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"\n"
"}\n"
"QPushButton:hover{    \n"
"    background-color: rgb(191, 191, 191);\n"
"    effect = QtWidgets.QGraphicsDropShadowEffect(QPushButton)\n"
"    effect.setOffset(0, 0)\n"
"    effect.setBlurRadius(20)\n"
"    effect.setColor(QColor(57, 219, 255))\n"
"    QPushButton.setGraphicsEffect(effect)")
        self.pushButton.setObjectName("pushButton")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "HOVER"))


# ++ vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
class PushButton(QtWidgets.QPushButton):
    hover = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(PushButton, self).__init__(parent)
        pass

    def enterEvent(self, event):
        self.hover.emit("enterEvent")

    def leaveEvent(self, event):
        self.hover.emit("leaveEvent")
# ++ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


class ExampleApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton.setCheckable(True)

        # Синяя кнопка границы
        self.aniButton = AnimationShadowEffect(QtCore.Qt.blue, self.pushButton)

#        self.pushButton.clicked.connect(self.button_state_func)
        self.pushButton.hover.connect(self.button_hover)                          # +++

        self.pushButton.setGraphicsEffect(self.aniButton)
#        self.aniButton.start()

# ++ vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    def button_state_func(self, state):
        if state: self.aniButton.stop()
        else: self.aniButton.start()

    def button_hover(self, hover):
        if hover == "enterEvent" : self.aniButton.start()
        elif hover == "leaveEvent" : self.aniButton.stop()
# ++ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


if __name__=="__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    sys.exit(app.exec_()) 