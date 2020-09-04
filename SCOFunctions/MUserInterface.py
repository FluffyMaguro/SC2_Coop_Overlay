import sys
from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from SCOFunctions.MFilePath import innerPath
from SCOFunctions.MLogging import logclass

logger = logclass('UI','INFO')


class PlayerEntry:
    def __init__(self, name, wins, losses, note, index, parent):
        self.name = name
        self.wins = wins
        self.losses = losses
        self.winrate = 100*wins/(wins+losses)
        self.note = note
        self.index = index

        height = 30
        line_spacing = 7

        self.widget = QtWidgets.QWidget(parent)
        self.widget.setGeometry(QtCore.QRect(40, (self.index+1)*40, 860, height))
        self.widget.setMinimumHeight(height)
        self.widget.setMaximumHeight(height)

        self.line = QtWidgets.QFrame(self.widget)
        self.line.setGeometry(QtCore.QRect(10, 0, 760, 2))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.la_name = QtWidgets.QLabel(self.widget)
        self.la_name.setGeometry(QtCore.QRect(20, line_spacing, 150, 21))
        self.la_name.setText(self.name)

        self.la_wins = QtWidgets.QLabel(self.widget)
        self.la_wins.setGeometry(QtCore.QRect(220, line_spacing, 31, 21))
        self.la_wins.setAlignment(QtCore.Qt.AlignCenter)
        self.la_wins.setText(str(self.wins))

        self.la_losses = QtWidgets.QLabel(self.widget)
        self.la_losses.setGeometry(QtCore.QRect(280, line_spacing, 41, 21))
        self.la_losses.setAlignment(QtCore.Qt.AlignCenter)
        self.la_losses.setText(str(self.losses))

        self.la_winrate = QtWidgets.QLabel(self.widget)
        self.la_winrate.setGeometry(QtCore.QRect(350, line_spacing, 51, 21))
        self.la_winrate.setAlignment(QtCore.Qt.AlignCenter)
        self.la_winrate.setText(f'{self.winrate:.0f}%')

        self.ed_note = QtWidgets.QLineEdit(self.widget)
        self.ed_note.setGeometry(QtCore.QRect(480, line_spacing, 281, 21))
        self.ed_note.setAlignment(QtCore.Qt.AlignCenter)
        self.ed_note.setStyleSheet('color: #444')
        if not self.note in {None,''}:
            self.ed_note.setText(self.note)

        # This is necessary only sometimes (when the user is looking at the tab while its updating )
        for item in {self.widget, self.line, self.la_name, self.la_wins, self.la_losses, self.la_winrate, self.ed_note}:
            item.show()

    def get_note(self):
        return self.ed_note.text()

    def show(self):
        self.widget.show()

    def hide(self):
        self.widget.hide()

    def reposition(self, index):
        self.widget.move(40,(index+1)*40)


class WorkerSignals(QtCore.QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing, anything

    '''
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)


class Worker(QtCore.QRunnable):
    """
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    The function callback to run on this worker thread. Supplied args and kwargs will be passed through to the runner.
    `fn` function
    `arg` Arguments to pass to the callback function
    `kwargs` Keywords to pass to the callback function
    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()


    @QtCore.pyqtSlot()
    def run(self):
        """ Runs the function and emits signals (error, result, finished) """
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            logger.error(traceback.format_exc())
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


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
        self.tray_menu.setStyleSheet("background-color: #272E3B; color: #fff")

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


    # @QtCore.pyqtSlot(bool)    
    # def closeEvent(self, event):
    #     """ Overriding close event and minimizing instead """
    #     event.ignore()
    #     self.hide()
    #     self.show_minimize_message()


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
