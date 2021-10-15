import traceback
import keyboard
import urllib.request
from PyQt5 import QtWidgets, QtCore, QtGui

from SCOFunctions.MFilePath import innerPath
from SCOFunctions.MLogging import logclass, catch_exceptions
from SCOFunctions.Settings import Setting_manager as SM

logger = logclass('FAST', 'INFO')


class FastExpandSelector(QtWidgets.QWidget):
    # valid_maps and valid_commanders are used by outside functions
    valid_maps = {"Chain of Ascension", "Malwarfare", "Miner Evacuation", "Part and Parcel", "The Vermillion Problem"}
    valid_commanders = ("Alarak", "Karax", "Mengsk")
    padding = 6

    # Data will be received as [MapName, PlayerPosition]
    def __init__(self, parent=None):
        super().__init__()
        self.selectedMap = ""
        self.selectedCommander = ""
        self.selectedRace = ""
        self.playerPosition = 1
        self.hotkeys = []
        self.initUI()
        keyboard.add_hotkey("NUM 0", self.selectionMade, args=["cancel", 0])

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(self.padding, self.padding, self.padding, self.padding)
        spacer = 10

        # Set the title
        self.title = QtWidgets.QLabel()
        self.title.setStyleSheet("color: yellow; font-size:24px")
        layout.addWidget(self.title)

        # Set up the display label
        self.selectionText = QtWidgets.QLabel()
        self.selectionText.setStyleSheet("color:white; font-size:24px")
        layout.addWidget(self.selectionText)

        # Set up the image box that will be used to display the image
        self.pic = QtWidgets.QLabel()
        layout.addWidget(self.pic)

        # Set up the window
        self.setWindowTitle(f"Fast Expand Hints")
        self.setWindowIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowDoesNotAcceptFocus
                            | QtCore.Qt.WindowTransparentForInput)

        self.setStyleSheet("background-color: black;")
        sg = QtWidgets.QDesktopWidget().screenGeometry(int(SM.settings['monitor'] - 1))
        width = int(sg.width() * 425 / 1920)
        height = int(width * 270 / 425)
        self.setGeometry(0, 0, width, height)
        self.move(sg.bottomRight().x() - self.width(), sg.bottomRight().y() - self.height())
        self.setLayout(layout)

    def setData(self, data):
        """Set map and player position"""
        self.selectedMap = data[0]
        self.playerPosition = data[1]

    def showEvent(self, event):
        """Window is shown... start displaying selections"""
        self.generateCommanderList()

    @catch_exceptions(logger)
    def generateCommanderList(self):
        if self.selectedMap in {"Chain of Ascension", "Malwarfare", "Part and Parcel"}:
            commanderList = ["Alarak", "Karax", "Mengsk"]
        else:
            commanderList = ["Alarak", "Mengsk"]

        # Get a list of valid commanders to fast expand on map and generate a label and hook a hotkey
        labelString = ""
        for idx, commander in enumerate(commanderList):
            labelString += "NUM" + str(9 - idx) + " - " + commander + "\r\n"
            self.hotkeys.append(keyboard.add_hotkey("NUM " + str(9 - idx), self.selectionMade, args=["commander", commander.lower()]))

        # Add the Cancel option at the bottom
        labelString += "NUM0 - None"

        self.selectionText.setText(labelString)
        self.title.setText("Choose your commander:")

    @catch_exceptions(logger)
    def generateRaceList(self):
        if self.selectedMap in {"Chain of Ascension", "Malwarfare", "The Vermillion Problem"}:
            raceList = ["Protoss", "Terran", "Zerg"]
        elif self.selectedMap == "Part and Parcel":
            if self.selectedCommander == "Alarak":
                raceList = ["Protoss", "Terran"]
            else:
                raceList = ["Protoss", "Terran", "Zerg"]
        else:
            self.clearHotkeys()
            self.showExpand()
            return

        # Get a list of valid commanders to fast expand on map and generate a label and hook a hotkey
        labelString = ""
        for idx, race in enumerate(raceList):
            labelString += "NUM" + str(9 - idx) + " - " + race + "\r\n"
            self.hotkeys.append(keyboard.add_hotkey("NUM " + str(9 - idx), self.selectionMade, args=["race", race.lower()]))

        # Add the Cancel option at the bottom
        labelString += "NUM0 - None"

        # Add the label to the layout
        self.selectionText.setText(labelString)
        self.title.setText("Choose enemy race:")

    def showExpand(self):
        try:
            baseURL = "https://starcraft2coop.com/images/assistant/"
            filename = self.selectedCommander + "_"
            # Set up the file name to be called from starcraft2coop.com
            if self.selectedMap == "Chain of Ascension":
                filename += f"coa_{self.selectedRace}_{self.playerPosition}.jpg"
            elif self.selectedMap == "Malwarfare":
                filename += f"mw_{self.selectedRace}_{self.playerPosition}.jpg"
            elif self.selectedMap == "Miner Evacuation":
                filename += "me_.jpg"
            elif self.selectedMap == "Part and Parcel":
                filename += f"pp_{self.selectedRace}.jpg"
            elif self.selectedMap == "The Vermillion Problem":
                filename += f"tvp_{self.selectedRace}.jpg"

            # Get the image from the URL and display it
            url = baseURL + filename
            req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
            data = urllib.request.urlopen(req).read()
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(data)
            pixmap = pixmap.scaled(self.width() - self.padding, self.height() - 41, QtCore.Qt.KeepAspectRatio)
            self.pic.setPixmap(pixmap)
            self.selectionText.hide()
            self.title.setText("NUM0 - Close")
            self.title.setStyleSheet("color:white; font-size: 18px")
        except Exception:
            logger.error(traceback.format_exc)
            self.clearHotkeys()
            self.hide()
            self.reset()

    def selectionMade(self, action, selection):
        # Remove all hotkeys first
        self.clearHotkeys()
        # If a "close" action was sent, hide the window, then reset all components so they're ready for the next run0
        if action == "cancel" and self.isVisible():
            self.hide()
            self.reset()
        elif action == "commander":
            self.selectedCommander = selection
            self.generateRaceList()
        elif action == "race":
            self.selectedRace = selection
            self.showExpand()

    def reset(self):
        # Reset everything back to normal
        self.title.setStyleSheet("color:yellow; font-size:24px")
        self.selectionText.show()
        pixmap = QtGui.QPixmap()
        self.pic.setPixmap(pixmap)
        self.selectedMap = ""
        self.selectedCommander = ""
        self.selectedRace = ""
        self.playerPosition = 1

    @catch_exceptions(logger)
    def clearHotkeys(self):
        for hotkey in self.hotkeys:
            keyboard.remove_hotkey(hotkey)
        self.hotkeys = []
