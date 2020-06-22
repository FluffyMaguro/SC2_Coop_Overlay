import os
import sys
import json
import string
import traceback
import threading
import configparser
import ctypes.wintypes

import requests
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, QtGui

from MLogging import logclass
from SCOFunctions import check_replays, server_thread, keyboard_thread_SHOW, keyboard_thread_HIDE, set_initMessage, keyboard_thread_NEWER, keyboard_thread_OLDER, set_PLAYER_NAMES


APPVERSION = 12
version_link = 'https://github.com/FluffyMaguro/SC2_Coop_overlay/raw/master/version.txt'
github_link = 'https://github.com/FluffyMaguro/SC2_Coop_overlay/'
logger = logclass('SCO','INFO')
logclass.FILE = "SCO_log.txt"

### CONFIG SETUP
if not(os.path.isfile('SCO_config.ini')):
    with open('SCO_config.ini','w') as file:
        file.write("""[CONFIG] //Changes take effect the next time you start the app!\n\nPLAYER_NAMES = Maguro,BigMaguro\nDURATION = 60\nMONITOR = 1\n\nKEY_SHOW = Ctrl+/\nKEY_HIDE = Ctrl+*\nKEY_NEWER = Alt+/\nKEY_OLDER = Alt+*\n\nP1COLOR = #0080F8\nP2COLOR = #00D532\nAMONCOLOR = #FF0000\nMASTERYCOLOR = #FFDC87\n\nAOM_NAME = \nAOM_SECRETKEY = \n\nSHOWOVERLAY = True\nLOGGING = False""")

config = configparser.ConfigParser()
try:
    config.read('SCO_config.ini')
except:
    logger.error(traceback.format_exc())


def get_configvalue(name,default,section='CONFIG'):
    """ function to get values out of the config file in the correct type"""
    try:
        if name in config[section]:
            if config[section][name].strip() != '':
                #bools (this need to be infront on ints, as 'True' isintance of 'int' as well.)
                if isinstance(default, bool):
                    if config[section][name].strip().lower() in ['false','0','no']:
                        return False
                    else:
                        return True
                #integers
                elif isinstance(default, int):
                    try:
                        return int(config[section][name].strip(),10)
                    except:
                        return default
                #lists        
                elif isinstance(default, list):
                    return [i.strip() for i in config[section][name].split(',')]
                    
                #return as string
                else:
                    return config[section][name].strip()
    except:
        pass
    return default


def get_account_dir(path):
    """ function that locates StarCraft account directory """

    #if one is specified, use that
    if path != None and os.path.isdir(path):
        return path

    #use ctypes.wintypes instad of expanduser to get current documents folder
    CSIDL_PERSONAL = 5       # My Documents
    SHGFP_TYPE_CURRENT = 1   # Get current, not default value
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    user_folder = buf.value.replace('Documents','')

    #typical folder location
    account_path = os.path.join(user_folder,'Documents\\StarCraft II\\Accounts')
    if os.path.isdir(account_path):
        return account_path

    #one drive location
    account_path = os.path.join(user_folder,'OneDrive\\Documents\\StarCraft II\\Accounts')
    if os.path.isdir(account_path):
        return account_path

    #check in all current user folders
    for root, directories, files in os.walk(user_folder):
        for file in files:
            if file.endswith('.SC2Replay') and 'StarCraft II\\Accounts' in root:
                account_path = os.path.join(root,file).split('StarCraft II\\Accounts')[0]
                account_path += 'StarCraft II\\Accounts'
                with open('SCO_config.ini','a') as f:
                    f.write(f'\nACCOUNTDIR = {account_path}')
                return account_path

    #check in all drives
    available_drives = [f'{d}:\\' for d in string.ascii_uppercase if os.path.exists(f'{d}:\\')]
    for drive in available_drives:
        for root, directories, files in os.walk(drive):
            for file in files:
                if file.endswith('.SC2Replay') and 'StarCraft II\\Accounts' in root:
                    account_path = os.path.join(root,file).split('StarCraft II\\Accounts')[0]
                    account_path += 'StarCraft II\\Accounts'
                    with open('SCO_config.ini','a') as f:
                        f.write(f'\nACCOUNTDIR = {account_path}')
                    return account_path

    logger.error('Failed to find any StarCraft II account directory')
    return ''


ACCOUNTDIR = get_account_dir(get_configvalue('ACCOUNTDIR', None))
SHOWOVERLAY = get_configvalue('SHOWOVERLAY', True)
PLAYER_NAMES = get_configvalue('PLAYER_NAMES', [])
DURATION = get_configvalue('DURATION', 60)
KEY_SHOW = get_configvalue('KEY_SHOW', None)
KEY_HIDE = get_configvalue('KEY_HIDE', None)
KEY_OLDER = get_configvalue('KEY_OLDER', None)
KEY_NEWER = get_configvalue('KEY_NEWER', None)
P1COLOR = get_configvalue('P1COLOR', 'null')
P2COLOR = get_configvalue('P2COLOR', 'null')
AMONCOLOR = get_configvalue('AMONCOLOR', 'null')
MASTERYCOLOR = get_configvalue('MASTERYCOLOR', 'null')
AOM_NAME = get_configvalue('AOM_NAME', None)
AOM_SECRETKEY = get_configvalue('AOM_SECRETKEY', None)
LOGGING = get_configvalue('LOGGING', False)
PORT = get_configvalue('PORT', 7305)
MONITOR = get_configvalue('MONITOR', 1)
UNIFIEDHOTKEY = get_configvalue('UNIFIEDHOTKEY', True)

logclass.LOGGING = LOGGING
logger.info(f'\n{PORT=}\n{SHOWOVERLAY=}\n{PLAYER_NAMES=}\n{KEY_SHOW=}\n{KEY_HIDE=}\n{KEY_OLDER=}\n{KEY_NEWER=}\n{DURATION=}\n{AOM_NAME=}\nAOM_SECRETKEY set: {bool(AOM_SECRETKEY)}\n{UNIFIEDHOTKEY=}\n{LOGGING=}\n{ACCOUNTDIR=}\n--------')
set_PLAYER_NAMES(PLAYER_NAMES)


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
    """ expanding this class to add JS after page is loaded. This is used to distinquish main overlay from other overlays (e.g. in OBS)"""
    def __init__(self, unified, dll, parent=None):
        super().__init__(parent)
        self.loadFinished.connect(self.on_load_finished)
        self.unified = unified
        self.dll = dll


    @QtCore.pyqtSlot(bool)
    def on_load_finished(self,ok):
        if ok:
            self.page().runJavaScript(f"showmutators = false; showNotification(); fillhotkeyinfo('{KEY_SHOW}','{KEY_HIDE}','{KEY_NEWER}','{KEY_OLDER}',{'true' if self.unified else 'false'},{'true' if self.dll else 'false'});")


def getIconFile(file):
    """ get path to file when it's packaged with pyinstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.normpath(os.path.join(sys._MEIPASS, 'src', file))
    return f'src/{file}'


def startThreads():
    """ threading moved to this function so I can import main function without threading """
    t1 = threading.Thread(target = check_replays, daemon=True, args=(ACCOUNTDIR,AOM_NAME,AOM_SECRETKEY))
    t1.start()
    t2 = threading.Thread(target = server_thread, daemon=True, args=(PORT,))
    t2.start()

    if KEY_SHOW != None:
        t3 = threading.Thread(target = keyboard_thread_SHOW, daemon=True, args=(KEY_SHOW,))
        t3.start()

    if KEY_HIDE != None:
        t4 = threading.Thread(target = keyboard_thread_HIDE, daemon=True, args=(KEY_HIDE,))
        t4.start()

    if KEY_NEWER != None:
        t5 = threading.Thread(target = keyboard_thread_NEWER, daemon=True, args=(KEY_NEWER,))
        t5.start()

    if KEY_OLDER != None:
        t6 = threading.Thread(target = keyboard_thread_OLDER, daemon=True, args=(KEY_OLDER,))
        t6.start()



def main(startthreads=True):
    download_link = new_version()
    app = QtWidgets.QApplication(sys.argv)
    view = WWW(UNIFIEDHOTKEY,download_link)

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
        sg = QtWidgets.QDesktopWidget().screenGeometry(MONITOR-1)
        logger.info(f'Using monitor {MONITOR} ({sg.width()}x{sg.height()})')
        view.setFixedSize(sg.width()-1, sg.height())
        view.move(sg.left()+1,sg.top())

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

    set_initMessage([P1COLOR,P2COLOR,AMONCOLOR,MASTERYCOLOR], DURATION, UNIFIEDHOTKEY)

    if startthreads:        
        startThreads()            

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()