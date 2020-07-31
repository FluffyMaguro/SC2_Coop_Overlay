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
from SCOFunctions import check_for_new_game, check_replays, server_thread, keyboard_thread_SHOW, keyboard_thread_HIDE, set_initMessage, keyboard_thread_NEWER, keyboard_thread_OLDER, set_PLAYER_NAMES


APPVERSION = 16
version_link = 'https://github.com/FluffyMaguro/SC2_Coop_overlay/raw/master/version.txt'
github_link = 'https://github.com/FluffyMaguro/SC2_Coop_overlay/'
logger = logclass('SCO','INFO')
logclass.FILE = "SCO_log.txt"


def config_setup():
    """ Config setup """
    if not(os.path.isfile('SCO_config.ini')):
        with open('SCO_config.ini','w') as file:
            file.write("""[CONFIG] //Changes take effect the next time you start the app!\n\nPLAYER_NAMES = Maguro,BigMaguro\nDURATION = 60\nMONITOR = 1\n\nKEY_SHOW = Ctrl+/\nKEY_HIDE = Ctrl+*\nKEY_NEWER = Alt+/\nKEY_OLDER = Alt+*\n\nP1COLOR = #0080F8\nP2COLOR = #00D532\nAMONCOLOR = #FF0000\nMASTERYCOLOR = #FFDC87\n\nAOM_NAME = \nAOM_SECRETKEY = \n\nSHOWOVERLAY = True\nLOGGING = False""")

    config = configparser.ConfigParser()
    try:
        config.read('SCO_config.ini')
    except:
        logger.error(traceback.format_exc())

    return config


def get_configvalue(config,name,default,section='CONFIG'):
    """ Gets values out of the config file in the correct type"""
    try:
        if name in config[section]:
            if config[section][name].strip() != '':
                # Bools (this need to be infront on ints, as 'True' isintance of 'int' as well.)
                if isinstance(default, bool):
                    if config[section][name].strip().lower() in ['false','0','no']:
                        return False
                    else:
                        return True
                # Integers
                elif isinstance(default, int) or isinstance(default, float):
                    try:
                        return float(config[section][name].strip())
                    except:
                        return default
                # Lists        
                elif isinstance(default, list):
                    return [i.strip() for i in config[section][name].split(',')]
                    
                # Return as string
                else:
                    return config[section][name].strip()
    except:
        pass
    return default


def get_account_dir(path):
    """ Locates StarCraft account directory """

    # If one is specified, use that
    if path != None and os.path.isdir(path):
        return path

    # Use ctypes.wintypes instad of expanduser to get current documents folder
    CSIDL_PERSONAL = 5       # My Documents
    SHGFP_TYPE_CURRENT = 1   # Get current, not default value
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    user_folder = buf.value.replace('Documents','')

    # Typical folder location
    account_path = os.path.join(user_folder,'Documents\\StarCraft II\\Accounts')
    if os.path.isdir(account_path):
        return account_path

    # One drive location
    account_path = os.path.join(user_folder,'OneDrive\\Documents\\StarCraft II\\Accounts')
    if os.path.isdir(account_path):
        return account_path

    # Check in all current user folders
    for root, directories, files in os.walk(user_folder):
        for file in files:
            if file.endswith('.SC2Replay') and 'StarCraft II\\Accounts' in root:
                account_path = os.path.join(root,file).split('StarCraft II\\Accounts')[0]
                account_path += 'StarCraft II\\Accounts'
                with open('SCO_config.ini','a') as f:
                    f.write(f'\nACCOUNTDIR = {account_path}')
                return account_path

    # Check in all drives
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


def new_version():
    """ Checks for a new version of the app """
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
    """ Expanding this class to add javascript after page is loaded. This is used to distinquish main overlay from other overlays (e.g. in OBS)"""
    def __init__(self, unified, dll, KEY_SHOW, KEY_HIDE, KEY_NEWER, KEY_OLDER, parent=None):
        super().__init__(parent)
        self.loadFinished.connect(self.on_load_finished)
        self.unified = unified
        self.dll = dll
        self.KEY_SHOW = KEY_SHOW
        self.KEY_HIDE = KEY_HIDE
        self.KEY_NEWER = KEY_NEWER
        self.KEY_OLDER = KEY_OLDER

    @QtCore.pyqtSlot(bool)
    def on_load_finished(self,ok):
        if ok:
            self.page().runJavaScript(f"showmutators = false; showNotification(); fillhotkeyinfo('{self.KEY_SHOW}','{self.KEY_HIDE}','{self.KEY_NEWER}','{self.KEY_OLDER}',{'true' if self.unified else 'false'},{'true' if self.dll else 'false'});")


def startThreads(ACCOUNTDIR,AOM_NAME,AOM_SECRETKEY,PORT,KEY_SHOW,KEY_HIDE,KEY_NEWER,KEY_OLDER,PLAYER_WINRATES):
    """ Threading moved to this function so I can import main function without threading """
    t1 = threading.Thread(target = check_replays, daemon=True, args=(ACCOUNTDIR,AOM_NAME,AOM_SECRETKEY,PLAYER_WINRATES))
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

    if PLAYER_WINRATES:
        t7 = threading.Thread(target = check_for_new_game, daemon=True)
        t7.start()


def main(startthreads=True):

    # Start by testing write permissions
    permission_error = False
    try:
        with open(logclass.FILE,'a') as file:
            file.write('--------\nStarting...\n')
    except:
        permission_error = True
        logger.info(f'Persmission error:\n{traceback.format_exc()}')


    # Lets start by initinalizing config file an getting values from it
    config = config_setup()
    ACCOUNTDIR = get_account_dir(get_configvalue(config,'ACCOUNTDIR', None))
    SHOWOVERLAY = get_configvalue(config,'SHOWOVERLAY', True)
    PLAYER_NAMES = get_configvalue(config,'PLAYER_NAMES', [])
    DURATION = get_configvalue(config,'DURATION', 60)
    KEY_SHOW = get_configvalue(config,'KEY_SHOW', None)
    KEY_HIDE = get_configvalue(config,'KEY_HIDE', None)
    KEY_OLDER = get_configvalue(config,'KEY_OLDER', None)
    KEY_NEWER = get_configvalue(config,'KEY_NEWER', None)
    P1COLOR = get_configvalue(config,'P1COLOR', 'null')
    P2COLOR = get_configvalue(config,'P2COLOR', 'null')
    AMONCOLOR = get_configvalue(config,'AMONCOLOR', 'null')
    MASTERYCOLOR = get_configvalue(config,'MASTERYCOLOR', 'null')
    AOM_NAME = get_configvalue(config,'AOM_NAME', None)
    AOM_SECRETKEY = get_configvalue(config,'AOM_SECRETKEY', None)
    LOGGING = get_configvalue(config,'LOGGING', False)
    PORT = get_configvalue(config,'PORT', 7305)
    MONITOR = get_configvalue(config,'MONITOR', 1)
    UNIFIEDHOTKEY = get_configvalue(config,'UNIFIEDHOTKEY', True)
    OWIDTH = get_configvalue(config,'OWIDTH', 0.5)
    OHEIGHT = get_configvalue(config,'OHEIGHT', 1)
    OFFSET = get_configvalue(config,'OFFSET', 0)
    PLAYER_WINRATES = get_configvalue(config,'PLAYER_WINRATES', False)


    logclass.LOGGING = False if permission_error else LOGGING
    logger.info(f'\n{PORT=}\n{MONITOR=}\n{PLAYER_WINRATES=}\n{SHOWOVERLAY=}\n{PLAYER_NAMES=}\n{KEY_SHOW=}\n{KEY_HIDE=}\n{KEY_OLDER=}\n{KEY_NEWER=}\n{DURATION=}\n{AOM_NAME=}\nAOM_SECRETKEY set: {bool(AOM_SECRETKEY)}\n{UNIFIEDHOTKEY=}\n{LOGGING=}\n{ACCOUNTDIR=}\n{OWIDTH=}\n{OHEIGHT=}\n{OFFSET=}\n--------')

    # Set player names in SCOFunctions
    set_PLAYER_NAMES(PLAYER_NAMES)

    # Check for a new version
    download_link = new_version()
    # Init the app and QWebEngineView
    app = QtWidgets.QApplication(sys.argv)
    view = WWW(UNIFIEDHOTKEY, download_link, KEY_SHOW, KEY_HIDE, KEY_NEWER, KEY_OLDER)
    # Set flags, this might work only on Windows 10
    view.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowTransparentForInput|QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.CoverWindow)
    view.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
    
    # Create the system tray
    tray = QtWidgets.QSystemTrayIcon()
    # Add the icon either from the packaged file or from the directory
    if os.path.isfile('OverlayIcon.ico'):
        tray.setIcon(QtGui.QIcon("OverlayIcon.ico"))
    else:
       tray.setIcon(QtGui.QIcon(os.path.join(sys._MEIPASS,'src/OverlayIcon.ico')))
    tray.setVisible(True)
    tray.setToolTip(f'StarCraft Co-op Overlay 1.{APPVERSION}')
        
    # Add icons to the system tray
    menu = QtWidgets.QMenu()

    # 1.Link to github
    SCO = QtWidgets.QAction("StarCraft II Co-op Overlay")
    SCO.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_ToolBarHorizontalExtensionButton')))
    SCO.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(github_link)))
    menu.addAction(SCO)
    menu.addSeparator()

    # 2.Config file
    config_file = QtWidgets.QAction(f"Config file")
    config_file.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DirIcon')))
    config_file_path = os.path.join(os.getcwd(),"SCO_config.ini")
    config_file.triggered.connect(lambda: os.startfile(config_file_path,'open'))
    menu.addAction(config_file)
    menu.addSeparator()

    # 3.Update link
    if download_link:
        update = QtWidgets.QAction("New version available!")
        update.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(download_link)))
        update.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_ArrowUp')))
    else:
        update = QtWidgets.QAction(f"Up-to-date (1.{APPVERSION})")
        update.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DialogApplyButton')))
    menu.addAction(update)
    menu.addSeparator()

    # 4.Quit
    quit = QtWidgets.QAction("Quit")
    quit.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DialogCancelButton')))
    quit.triggered.connect(app.quit)
    menu.addAction(quit)
    tray.setContextMenu(menu)

    # 5.Permission error
    if permission_error:
        perError = QtWidgets.QAction("Permission error! Exclude app folder in antivirus")
        perError.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_MessageBoxWarning')))
        tray.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_MessageBoxWarning')))
        menu.addAction(perError)
        menu.addSeparator()    

    # Show overlay if it's not set otherwise
    if SHOWOVERLAY and not permission_error:
        webpage = view.page()
        webpage.setBackgroundColor(QtCore.Qt.transparent)

        # Set correct size and width for the widget; Setting it to full shows black screen on my machine, works fine on notebook (thus -1 offset)
        sg = QtWidgets.QDesktopWidget().screenGeometry(int(MONITOR-1))
        logger.info(f'Using monitor {int(MONITOR)} ({sg.width()}x{sg.height()})')
        view.setFixedSize(int(sg.width()*OWIDTH-1), int(sg.height()*OHEIGHT))
        view.move(int(sg.width()*(1-OWIDTH)-OFFSET+1),sg.top())

        # Load webpage
        if os.path.isfile('Layouts/Layout.html'):
            path = os.path.join(os.getcwd(),'Layouts/Layout.html')
            view.load(QtCore.QUrl().fromLocalFile(path))
            view.show()
        else:
            # 6. Layout file error
            logger.error("Error! Failed to locate the html file")
            menu.addSeparator()
            error = QtWidgets.QAction("Error! Failed to locate the html file")
            error.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_MessageBoxWarning')))
            tray.setIcon(view.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_MessageBoxWarning')))
            error.triggered.connect(app.quit)
            menu.addAction(error)

    # Send init message to all connected layouts, not just the one created as overlay
    set_initMessage([P1COLOR,P2COLOR,AMONCOLOR,MASTERYCOLOR], DURATION, UNIFIEDHOTKEY)

    if startthreads and not permission_error:        
        startThreads(ACCOUNTDIR,AOM_NAME,AOM_SECRETKEY,PORT,KEY_SHOW,KEY_HIDE,KEY_NEWER,KEY_OLDER,PLAYER_WINRATES)            

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()