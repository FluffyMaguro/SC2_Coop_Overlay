import os
import sys
import json
import threading
import configparser

import requests
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, QtGui

from MLogging import logclass
from SCOFunctions import check_replays, server_thread, keyboard_thread_SHOW, keyboard_thread_HIDE


APPVERSION = 7
PORT = 7305
version_link = 'https://github.com/FluffyMaguro/SC2_Coop_overlay/raw/master/version.txt'
github_link = 'https://github.com/FluffyMaguro/SC2_Coop_overlay/'
logger = logclass('SCO','INFO')
logclass.FILE = "SCO_log.txt"

### CONFIG SETUP
if not(os.path.isfile('SCO_config.ini')):
    with open('SCO_config.ini','w') as file:
        file.write("""[CONFIG]\nSHOWOVERLAY = True""")

config = configparser.ConfigParser()
config.read('SCO_config.ini')


def get_configvalue(name,default,section='CONFIG'):
    """ function to get values out of the config file in the correct type"""
    if name in config[section]:
        if config[section][name].strip() != '':
            #integers
            if isinstance(default, int):
                try:
                    return int(config[section][name].strip())
                except:
                    return default
            #lists        
            elif isinstance(default, list):
                return [i.strip() for i in config[section][name].split(',')]
            #bools    
            elif isinstance(default, bool):
                if config[section][name].strip().lower() in ['false','0','no']:
                    return False
                else:
                    return True
            #return as string
            else:
                return config[section][name].strip()
    return default


ACCOUNTDIR = get_configvalue('ACCOUNTDIR', os.path.join(os.path.expanduser('~'),'Documents\\StarCraft II\\Accounts'))
REPLAYTIME = get_configvalue('REPLAYTIME', 60)
SHOWOVERLAY = get_configvalue('SHOWOVERLAY', True)
PLAYER_NAMES = get_configvalue('PLAYER_NAMES', [])
DURATION = get_configvalue('DURATION', 60)
KEY_SHOW = get_configvalue('KEY_SHOW', None)
KEY_HIDE = get_configvalue('KEY_HIDE', None)
P1COLOR = get_configvalue('P1COLOR', None)
P2COLOR = get_configvalue('P2COLOR', None)
AMONCOLOR = get_configvalue('AMONCOLOR', None)
MASTERYCOLOR = get_configvalue('MASTERYCOLOR', None)
AOM_NAME = get_configvalue('AOM_NAME', None)
AOM_SECRETKEY = get_configvalue('AOM_SECRETKEY', None)
LOGGING = get_configvalue('LOGGING', False)

logclass.LOGGING = LOGGING
logger.info(f'\n{SHOWOVERLAY=}\n{PLAYER_NAMES=}\n{KEY_SHOW=}\n{KEY_HIDE=}\n{DURATION=}\n{REPLAYTIME=}\n{AOM_NAME=}\nAOM_SECRETKEY set: {bool(AOM_SECRETKEY)}\n{LOGGING=}\n{ACCOUNTDIR=}\n--------')


def getColorCommands():
    """ prepares javascript function for setting colors """
    command = 'setColors('
    command += f"'{P1COLOR}'," if P1COLOR != None else 'null,'
    command += f"'{P2COLOR}'," if P2COLOR != None else 'null,'
    command += f"'{AMONCOLOR}'," if AMONCOLOR != None else 'null,'
    command += f"'{MASTERYCOLOR}'" if MASTERYCOLOR != None else 'null'
    command += ');'
    return command


def new_version():
    """ checks for a new version of the app """
    try:
        data = json.loads(requests.get(version_link).text)
        logger.info(f'This version: 1.{APPVERSION}. Most current live version: 1.{data["version"]}. ')
        if data['version'] > APPVERSION:        
            return data['download_link_1']
        else:
            return False
    except:
        logger.error('Failed to check for the new version')
        return False


class WWW(QtWebEngineWidgets.QWebEngineView):
    """ expanding this class to add JS after page is loaded"""
    def __init__(self,parent=None):
        super().__init__(parent)
        self.loadFinished.connect(self.on_load_finished)


    @QtCore.pyqtSlot(bool)
    def on_load_finished(self,ok):
        if ok:
            self.page().runJavaScript(f"showmutators = false; PORT = {PORT}; DURATION = {DURATION}; {getColorCommands()}")


def getIconFile(file):
    """ get path to file when it's packaged with pyinstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.normpath(os.path.join(sys._MEIPASS, 'src', file))
    return f'src/{file}'


def startThreads():
    """ threading moved to this function so I can import main function without threading """
    t1 = threading.Thread(target = check_replays, daemon=True, args=(ACCOUNTDIR,PLAYER_NAMES,REPLAYTIME,AOM_NAME,AOM_SECRETKEY))
    t1.start()
    t2 = threading.Thread(target = server_thread, daemon=True, args=(PORT,))
    t2.start()

    if KEY_SHOW != None:
        t3 = threading.Thread(target = keyboard_thread_SHOW, daemon=True, args=(KEY_SHOW,))
        t3.start()

    if KEY_HIDE != None:
        t4 = threading.Thread(target = keyboard_thread_HIDE, daemon=True, args=(KEY_HIDE,))
        t4.start()


def main(startthreads=True):
    app = QtWidgets.QApplication(sys.argv)
    view = WWW()

    view.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowTransparentForInput|QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.CoverWindow)
    view.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
    
    ### Create the tray
    tray = QtWidgets.QSystemTrayIcon()
    if os.path.isfile('OverlayIcon.ico'):
        tray.setIcon(QtGui.QIcon("OverlayIcon.ico"))
    else:
        #if packaged file
        tray.setIcon(QtGui.QIcon(os.path.join(sys._MEIPASS,'src/OverlayIcon.ico')))
        
        
    tray.setVisible(True)
    menu = QtWidgets.QMenu()

    ### Link to github
    SCO = QtWidgets.QAction("StarCraft II Co-op Overlay")
    SCO.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_ToolBarHorizontalExtensionButton')))
    SCO.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(github_link)))
    menu.addAction(SCO)
    menu.addSeparator()

    ### Config
    config_file = QtWidgets.QAction(f"Config file")
    config_file.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DirIcon')))
    config_file_path = os.path.join(os.getcwd(),"SCO_config.ini")
    config_file.triggered.connect(lambda: os.startfile(config_file_path,'open'))
    menu.addAction(config_file)
    menu.addSeparator()

    ### Check for updates
    download_link = new_version()
    if download_link:
        update = QtWidgets.QAction("New version available!")
        update.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(download_link)))
        update.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_ArrowUp')))
    else:
        update = QtWidgets.QAction(f"Up-to-date (1.{APPVERSION})")
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

        ### Set correct size and width for the widget; Setting it to full shows black screen on my machine, works fine on notebook
        sg = QtWidgets.QDesktopWidget().screenGeometry()
        view.setFixedSize(sg.width()-1, sg.height())
        view.move(1,0)

        ### Load webpage
        if os.path.isfile('Layouts/Layout.html'):
            path = os.path.join(os.getcwd(),'Layouts/Layout.html')
            view.load(QtCore.QUrl().fromLocalFile(path))
            view.show()
        else:
            logger.error("Error! Failed to locate the html file")
            menu.addSeparator()
            error = QtWidgets.QAction("Error! Failed to locate the html file")
            error.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_MessageBoxWarning')))
            tray.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_MessageBoxWarning')))
            error.triggered.connect(app.quit)
            menu.addAction(error)

    if startthreads:        
        startThreads()            

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()