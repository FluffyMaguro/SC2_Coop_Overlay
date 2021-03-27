from PyQt5 import QtWidgets, QtCore


class FastExpandSelector(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.initUI()

    def initUI(self):
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowTransparentForInput | QtCore.Qt.WindowStaysOnTopHint
        #                     | QtCore.Qt.CoverWindow | QtCore.Qt.NoDropShadowWindowHint | QtCore.Qt.WindowDoesNotAcceptFocus)
        self.setGeometry(0, 0, 300, 200)
        self.setStyleSheet("background-color: orange;")
        sg = QtWidgets.QDesktopWidget().screenGeometry(0)
        self.move(sg.width() - self.width(), sg.bottom() - self.height())
