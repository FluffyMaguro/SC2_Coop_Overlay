from PyQt5 import QtWidgets, QtGui
from SCOFunctions.MFilePath import innerPath
 

class CustomKeySequenceEdit(QtWidgets.QKeySequenceEdit):
    def __init__(self, parent=None):
        super(CustomKeySequenceEdit, self).__init__(parent)
 
    def keyPressEvent(self, QKeyEvent):
        super(CustomKeySequenceEdit, self).keyPressEvent(QKeyEvent)
        value = self.keySequence()
        self.setKeySequence(QtGui.QKeySequence(value))


class CustomQTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super(CustomQTabWidget, self).__init__(parent)

        # Tray
        self.tray_icon = QtWidgets.QSystemTrayIcon()
        self.tray_icon.setIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        self.tray_menu = QtWidgets.QMenu()

        self.show_action = QtWidgets.QAction("Show")
        self.show_action.triggered.connect(self.show)
        self.show_action.setIcon(self.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_TitleBarMaxButton')))
        self.tray_menu.addAction(self.show_action)

        self.quit_action = QtWidgets.QAction("Quit")
        self.quit_action.setIcon(self.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DialogCancelButton')))
        self.quit_action.triggered.connect(QtWidgets.qApp.quit)
        self.tray_menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()


    def closeEvent(self, event):
        """ Overriding close event and minimizing instead """
        event.ignore()
        self.hide()
        self.show_minimize_message()


    def show_minimize_message(self):
        self.tray_icon.showMessage(
                "StarCraft Co-op Overlay",
                "App was minimized into the tray",
                QtGui.QIcon(innerPath('src/OverlayIcon.ico')),
                2000
            )


