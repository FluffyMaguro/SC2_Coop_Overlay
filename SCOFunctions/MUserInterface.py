from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from SCOFunctions.MFilePath import innerPath


class CustomKeySequenceEdit(QtWidgets.QKeySequenceEdit):
    def __init__(self, parent=None):
        super(CustomKeySequenceEdit, self).__init__(parent)
 
    def keyPressEvent(self, QKeyEvent):
        super(CustomKeySequenceEdit, self).keyPressEvent(QKeyEvent)
        value = self.keySequence()
        self.setKeySequence(QtGui.QKeySequence(value))


class CustomQTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None, settings=dict()):
        super(CustomQTabWidget, self).__init__(parent)

        # Tray
        self.tray_icon = QtWidgets.QSystemTrayIcon()
        self.tray_icon.setIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        self.tray_icon.activated.connect(self.tray_activated)
        self.tray_menu = QtWidgets.QMenu()

        self.show_action = QtWidgets.QAction("Show")
        self.show_action.triggered.connect(self.show)
        self.show_action.setIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        self.tray_menu.addAction(self.show_action)

        self.quit_action = QtWidgets.QAction("Quit")
        self.quit_action.setIcon(self.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DialogCancelButton')))
        self.quit_action.triggered.connect(QtWidgets.qApp.quit)
        self.tray_menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

        self.settings = settings


    @QtCore.pyqtSlot(bool)    
    def closeEvent(self, event):
        """ Overriding close event and minimizing instead """
        event.ignore()
        self.hide()
        self.show_minimize_message()


    def format_close_message(self):
        """ Shows few hotkeys in the notification area"""
        text = ''
        setting_dict = {"hotkey_show/hide":"Show/Hide","hotkey_newer":"Newer replay","hotkey_older":"Older replay"}
        for key in setting_dict:
            if key in self.settings and self.settings[key] != '':
                text += f"\n{self.settings[key]} → {setting_dict[key]}"
        return text


    def show_minimize_message(self, message=''):
        self.tray_icon.showMessage(
                "StarCraft Co-op Overlay",
                f"App was minimized into the tray{self.format_close_message()}",
                QtGui.QIcon(innerPath('src/OverlayIcon.ico')),
                2000
            )


    def tray_activated(self, reason):
        """ Hides/shows main window when the tray icon is double clicked """
        if reason == 2:
            if self.isVisible():
                self.hide()
            else:
                self.show()


class CustomWebView(QtWebEngineWidgets.QWebEngineView):
    """ Expanding this class to add javascript after page is loaded. This is could be used to distinquish main overlay from other overlays (e.g. in OBS)"""
    def __init__(self,  parent=None):
        super().__init__(parent)
        self.loadFinished.connect(self.on_load_finished)


    @QtCore.pyqtSlot(bool)
    def on_load_finished(self,ok):
        if ok:
            self.page().runJavaScript(f"showmutators = false;")
