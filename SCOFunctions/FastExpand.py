from PyQt5 import QtWidgets, QtCore, QtGui
import keyboard
import urllib.request


class FastExpandSelector(QtWidgets.QWidget):
    selectedMap = ""
    selectedCommander = ""
    selectedRace = ""
    playerPosition = "1"
    hotkeys = []
    #Data will be received as [MapName, PlayerPosition]
    def __init__(self, data, parent=None):
        super().__init__()
        self.selectedMap = data[0]
        self.playerPosition = data[1]
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        spacer = 10

        #Set the title
        self.title = QtWidgets.QLabel()
        self.title.setText("Make a selection")
        self.title.setStyleSheet("background-color:black;color:white;font-size:24px")
        layout.addWidget(self.title)

        #Set up the display label
        self.selectionText = QtWidgets.QLabel()
        self.selectionText.setStyleSheet("background-color:black;color:white;font-size:24px")
        layout.addWidget(self.selectionText)
<<<<<<< HEAD
        
=======

>>>>>>> 0bb79c21a7d35566c070b40100f9b27797e65dfc
        #Set up the image box that will be used to display the image
        self.pic = QtWidgets.QLabel()
        layout.addWidget(self.pic)

        #Set up commander list for selection
        try:
            self.generateCommanderList()
        except Exception as e:
            print(e)
<<<<<<< HEAD
                          
=======

>>>>>>> 0bb79c21a7d35566c070b40100f9b27797e65dfc
        #Set up the window
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowDoesNotAcceptFocus)
        self.setGeometry(0, 0, 425, 270)
        self.setStyleSheet("background-color: black;")
        sg = QtWidgets.QDesktopWidget().screenGeometry(0)
        self.move(sg.width() - self.width(), sg.bottom() - self.height())
        self.setLayout(layout)

    def generateCommanderList(self):
<<<<<<< HEAD
        if(self.selectedMap in ["Chain of Ascension", "Malwarfare", "Part and Parcel"]):
            commanderList = ["Alarak", "Karax", "Mengsk"]
        else:
            commanderList =  ["Alarak", "Mengsk"]
=======
        if (self.selectedMap in ["Chain of Ascension", "Malwarfare", "Part and Parcel"]):
            commanderList = ["Alarak", "Karax", "Mengsk"]
        else:
            commanderList = ["Alarak", "Mengsk"]
>>>>>>> 0bb79c21a7d35566c070b40100f9b27797e65dfc

        #Get a list of valid commanders to fast expand on map and generate a label and hook a hotkey
        count = 0
        labelString = ""
        for commander in commanderList:
<<<<<<< HEAD
            count +=1
=======
            count += 1
>>>>>>> 0bb79c21a7d35566c070b40100f9b27797e65dfc
            labelString += "NUM" + str(count) + " - " + commander + "\r\n"
            self.hotkeys.append(keyboard.add_hotkey("NUM " + str(count), self.selectionMade, args=["commander", commander.lower()]))

        #Add the Cancel option at the bottom and hook a hotkey
        labelString += "NUM0 - None"
        self.hotkeys.append(keyboard.add_hotkey("NUM 0", self.selectionMade, args=["cancel", 0]))

        self.selectionText.setText(labelString)
        return

    def generateRaceList(self):
<<<<<<< HEAD
        if(self.selectedMap in ["Chain of Ascension", "Malwarfare", "The Vermillion Problem"]):
            raceList = ["Protoss", "Terran", "Zerg"]
        elif(self.selectedMap == "Part and Parcel"):
            if(self.selectedCommander =="Alarak"):
=======
        if (self.selectedMap in ["Chain of Ascension", "Malwarfare", "The Vermillion Problem"]):
            raceList = ["Protoss", "Terran", "Zerg"]
        elif (self.selectedMap == "Part and Parcel"):
            if (self.selectedCommander == "Alarak"):
>>>>>>> 0bb79c21a7d35566c070b40100f9b27797e65dfc
                raceList = ["Protoss", "Terran"]
            else:
                raceList = ["Protoss", "Terran", "Zerg"]
        else:
            self.clearHotkeys()
            self.showExpand()
            return

        #Get a list of valid commanders to fast expand on map and generate a label and hook a hotkey
        count = 0
        labelString = ""
        for race in raceList:
<<<<<<< HEAD
            count +=1
=======
            count += 1
>>>>>>> 0bb79c21a7d35566c070b40100f9b27797e65dfc
            labelString += "NUM" + str(count) + " - " + race + "\r\n"
            self.hotkeys.append(keyboard.add_hotkey("NUM " + str(count), self.selectionMade, args=["race", race.lower()]))

        #Add the Cancel option at the bottom and hook a hotkey
        labelString += "NUM0 - None"
        self.hotkeys.append(keyboard.add_hotkey("NUM 0", self.selectionMade, args=["cancel", 0]))

        #Add the label to the layout
        self.selectionText.setText(labelString)
        return

    def showExpand(self):
        baseURL = "https://starcraft2coop.com/images/assistant/"
        filename = self.selectedCommander + "_"
        #Set up the file name to be called from starcraft2coop.com
        if (self.selectedMap == "Chain of Ascension"):
            filename += "coa_" + self.selectedRace + "_" + self.playerPosition + ".jpg"
        elif (self.selectedMap == "Malwarfare"):
            filename += "mw_" + self.selectedRace + "_" + self.playerPosition + ".jpg"
        elif (self.selectedMap == "Miner Evacuation"):
            filename += "me_.jpg"
        elif (self.selectedMap == "Part and Parcel"):
            filename += "pp_" + self.selectedRace + ".jpg"
<<<<<<< HEAD
        elif (self.selectedMap == "Miner Evacuation"):
            filename += "tvp_" + self.selectedRace + ".jpg"

        #Get the image from the URL and display it
        url = baseURL + filename   
        req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"}) 
        data = urllib.request.urlopen( req ).read()
=======
        elif (self.selectedMap == "The Vermillion Problem"):
            filename += "tvp_" + self.selectedRace + ".jpg"

        #Get the image from the URL and display it
        url = baseURL + filename
        req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
        data = urllib.request.urlopen(req).read()
>>>>>>> 0bb79c21a7d35566c070b40100f9b27797e65dfc
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(data)
        self.pic.setPixmap(pixmap)
        self.selectionText.hide()
<<<<<<< HEAD
        
=======

>>>>>>> 0bb79c21a7d35566c070b40100f9b27797e65dfc
        self.title.setText("NUM0 - Close")
        self.hotkeys.append(keyboard.add_hotkey("NUM 0", self.selectionMade, args=["cancel", 0]))
        self.title.setStyleSheet("background-color:black;color:white;font-size:12px")

<<<<<<< HEAD
    def selectionMade(self,action, selection):
        #Remove all hotkeys first
        self.clearHotkeys()
        #If a "close" action was sent, close the window
        if (action=="cancel"):
            self.close()
            return
        elif (action=="commander"):
            self.selectedCommander = selection
            self.generateRaceList()
        elif (action=="race"):
=======
    def selectionMade(self, action, selection):
        #Remove all hotkeys first
        self.clearHotkeys()
        #If a "close" action was sent, close the window
        if (action == "cancel"):
            self.close()
            return
        elif (action == "commander"):
            self.selectedCommander = selection
            self.generateRaceList()
        elif (action == "race"):
>>>>>>> 0bb79c21a7d35566c070b40100f9b27797e65dfc
            self.selectedRace = selection
            self.showExpand()

    def clearHotkeys(self):
        for hotkey in self.hotkeys:
            keyboard.remove_hotkey(hotkey)

        self.hotkeys = []
<<<<<<< HEAD
        return

=======
        return
>>>>>>> 0bb79c21a7d35566c070b40100f9b27797e65dfc
