import os
import sys
import json
import requests
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, QtGui

APPVERSION = 1
PORT = 7305
version_link = 'https://github.com/FluffyMaguro/SC2_Coop_overlay/raw/master/version.txt'
version_download = 'https://github.com/FluffyMaguro/SC2_Coop_overlay/'


def new_version():
    """ checks for a new version of the app """
    try:
        data = json.loads(requests.get(version_link).text)
        if data['version'] > APPVERSION:
            return True
        else:
            return False
    except:
        print('Failed to check for the new version')
        return False


class WWW(QtWebEngineWidgets.QWebEngineView):
    """ expanding this class to add JS after page is loaded"""
    def __init__(self,parent=None):
        super().__init__(parent)
        self.loadFinished.connect(self.on_load_finished)

    @QtCore.pyqtSlot(bool)
    def on_load_finished(self,ok):
        if ok:
            self.page().runJavaScript(f"showmutators = true; PORT = {PORT}")      
            pass


def main(showoverlay):
    app = QtWidgets.QApplication(sys.argv)
    view = WWW()

    view.setWindowFlags(QtCore.Qt.FramelessWindowHint|\
                        QtCore.Qt.WindowTransparentForInput|\
                        QtCore.Qt.WindowStaysOnTopHint|\
                        QtCore.Qt.CoverWindow) #Tool - hides from taskbar, but loses initial autofocus. Cover window works with autofocus.

    view.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
    
    ### Create the tray
    tray = QtWidgets.QSystemTrayIcon()
    tray.setIcon(QtGui.QIcon("Layouts/icon.png"))
    tray.setVisible(True)
    menu = QtWidgets.QMenu()

    ### Check for updates
    if new_version() == True:
        update = QtWidgets.QAction("New version available!")
        update.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(version_download)))
    else:
        update = QtWidgets.QAction("Up-to-date")
    menu.addAction(update)

    menu.addSeparator()

    ### Quit
    quit = QtWidgets.QAction("Quit")
    quit.triggered.connect(app.quit)
    menu.addAction(quit)
    tray.setContextMenu(menu)

    if showoverlay:
        webpage = view.page()
        webpage.setBackgroundColor(QtCore.Qt.transparent)
        # view.setStyleSheet("background:transparent; background-color:rgba(0,0,0,0)") #unnecessary

        ### Set correct size and width for the widget; Setting it to full shows black screen on my machine, works fine on notebook
        sg = QtWidgets.QDesktopWidget().screenGeometry()
        view.setFixedSize(sg.width()-1, sg.height())
        view.move(1,0)

        ### Load webpage
        path = os.path.join(os.getcwd(),'Layouts/Replay Analysis.html')
        view.load(QtCore.QUrl().fromLocalFile(path))

    
    view.show() #fullscreenshow makes it black on my main pc, works fine on notebook
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(False)