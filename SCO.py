import os
import sys
import json
import threading
import configparser

import requests
from SCOFunctions import check_replays, server_thread
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, QtGui


APPVERSION = 1
PORT = 7305
version_link = 'https://github.com/FluffyMaguro/SC2_Coop_overlay/raw/master/version.txt'
version_download = 'https://github.com/FluffyMaguro/SC2_Coop_overlay/'


### Config setup
if not(os.path.isfile('OverlayConfig.ini')):
    with open('OverlayConfig.ini','w') as file:
        file.write("""[CONFIG]\nSHOWOVERLAY = True""")

config = configparser.ConfigParser()
config.read('OverlayConfig.ini')

ACCOUNTDIR = os.path.join(os.path.expanduser('~'),'Documents\\StarCraft II\\Accounts')
if 'ACCOUNTDIR' in config['CONFIG']:
    ACCOUNTDIR = config['CONFIG']['ACCOUNTDIR']

SHOWOVERLAY = True
if 'SHOWOVERLAY' in config['CONFIG']:
    SHOWOVERLAY = config['CONFIG']['SHOWOVERLAY']
    if SHOWOVERLAY.lower() in ['false','0','no']:
        SHOWOVERLAY = False

PLAYER_NAMES = []
if 'PLAYER_NAMES' in config['CONFIG']:
    for player in config['CONFIG']['PLAYER_NAMES'].split(','):
        PLAYER_NAMES.append(player.strip())


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


def getIconFile(file):
    if hasattr(sys, '_MEIPASS'):
        return os.path.normpath(os.path.join(sys._MEIPASS, 'src', file))


def main():
    app = QtWidgets.QApplication(sys.argv)
    view = WWW()

    view.setWindowFlags(QtCore.Qt.FramelessWindowHint|\
                        QtCore.Qt.WindowTransparentForInput|\
                        QtCore.Qt.WindowStaysOnTopHint|\
                        QtCore.Qt.CoverWindow) #Tool - hides from taskbar, but loses initial autofocus. Cover window works with autofocus.

    view.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
    
    ### Create the tray
    tray = QtWidgets.QSystemTrayIcon()
    if os.path.isfile('OverlayIcon.ico'):
        tray.setIcon(QtGui.QIcon("OverlayIcon.ico"))
    else:
        # tray.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_FileDialogListView')))
        tray.setIcon(QtGui.QIcon(os.path.join(sys._MEIPASS,'src/OverlayIcon.ico')))
        
        
    tray.setVisible(True)
    menu = QtWidgets.QMenu()

    SCO = QtWidgets.QAction("StarCraft II Co-op Overlay")
    SCO.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_ToolBarHorizontalExtensionButton')))
    SCO.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(version_download)))
    menu.addAction(SCO)
    menu.addSeparator()
    
    ### Check for updates
    if new_version():
        update = QtWidgets.QAction("New version available!")
        update.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(version_download)))
        update.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_ArrowUp')))
    else:
        update = QtWidgets.QAction("Up-to-date")
        update.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DialogApplyButton')))
    menu.addAction(update)
    menu.addSeparator()

    ### Quit
    quit = QtWidgets.QAction("Quit")
    quit.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DialogCancelButton')))
    quit.triggered.connect(app.quit)
    menu.addAction(quit)
    tray.setContextMenu(menu)

    if SHOWOVERLAY:
        webpage = view.page()
        webpage.setBackgroundColor(QtCore.Qt.transparent)
        # view.setStyleSheet("background:transparent; background-color:rgba(0,0,0,0)") #unnecessary

        ### Set correct size and width for the widget; Setting it to full shows black screen on my machine, works fine on notebook
        sg = QtWidgets.QDesktopWidget().screenGeometry()
        view.setFixedSize(sg.width()-1, sg.height())
        view.move(1,0)

        ### Load webpage
        if os.path.isfile('Layouts/Replay Analysis.html'):
            path = os.path.join(os.getcwd(),'Layouts/Replay Analysis.html')
            view.load(QtCore.QUrl().fromLocalFile(path))
            view.show()
        else:
            print("Error! Failed to locate the html file")
            menu.addSeparator()
            error = QtWidgets.QAction("Error! Failed to locate the html file")
            error.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_MessageBoxWarning')))
            tray.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_MessageBoxWarning')))
            error.triggered.connect(app.quit)
            menu.addAction(error)


    t1 = threading.Thread(target = check_replays, daemon=True, args=(ACCOUNTDIR,PLAYER_NAMES,))
    t1.start()
    t2 = threading.Thread(target = server_thread, daemon=True, args=(PORT,))
    t2.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()