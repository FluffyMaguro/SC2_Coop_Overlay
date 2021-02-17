import traceback
from PyQt5 import QtWidgets, QtGui, QtCore
from SCOFunctions.MFilePath import innerPath, truePath


class DebugWindow(QtWidgets.QWidget):
    """ Window for debugging purposes"""
    def __init__(self, parent=None):
        super().__init__()
        self.p = parent

        self.setWindowTitle(f'Debug window')
        self.setWindowIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        self.setGeometry(1200, 1000, 600, 60)

        self.debug_code = QtWidgets.QLineEdit(self)
        self.debug_code.setGeometry(QtCore.QRect(0, 10, 450, 20))
        self.debug_code.setPlaceholderText('write code here')

        self.debug_button = QtWidgets.QPushButton(self)
        self.debug_button.setGeometry(QtCore.QRect(500, 10, 75, 25))
        self.debug_button.setText('Debug')
        self.debug_button.setShortcut("Return")
        self.debug_button.clicked.connect(self.run_script)

        self.result = QtWidgets.QLabel(self)
        self.result.setGeometry(QtCore.QRect(2, 35, 500, 20))

        self.show()

    def run_script(self):
        """ Debug function """
        text = self.debug_code.text()
        if text == 'keyboard':
            self.p.reset_keyboard_thread()
            return

        try:
            print(f'Executing: {text}')
            exec(text)
            self.result.setText(f'Executed: {text}')
        except:
            print(traceback.format_exc())
            self.result.setText(f'Failed to execute: {text}')