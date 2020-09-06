import os
import sys
import json
import shutil
import threading
import traceback
import urllib.request

import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets

import SCOFunctions.MUserInterface as MUI
import SCOFunctions.MainFunctions as MF
import SCOFunctions.HelperFunctions as HF
import SCOFunctions.MassReplayAnalysis as MR
from SCOFunctions.MLogging import logclass
from SCOFunctions.MFilePath import truePath, innerPath


logger = logclass('SCO','INFO')
logclass.FILE = truePath("Logs.txt")

APPVERSION = 119
SETTING_FILE = truePath('Settings.json')


class UI_TabWidget(object):
    def setupUI(self, TabWidget):
        TabWidget.setWindowTitle(f"StarCraft Co-op Overlay (v{str(APPVERSION)[0]}.{str(APPVERSION)[1:]})")
        TabWidget.setWindowIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        TabWidget.setFixedSize(980, 610)
        TabWidget.tray_icon.setToolTip(f'StarCraft Co-op Overlay {str(APPVERSION)[0]}.{str(APPVERSION)[1:]}')

        ##########################
        ######## MAIN TAB ########
        ##########################

        self.TAB_Main = QtWidgets.QWidget()

        # Start with Windows
        self.CH_StartWithWindows = QtWidgets.QCheckBox(self.TAB_Main)
        self.CH_StartWithWindows.setGeometry(QtCore.QRect(20, 20, 230, 17))
        self.CH_StartWithWindows.setText("Start with Windows")
        self.CH_StartWithWindows.setToolTip("The app will start automatically with the Windows")

        # Start minimized
        self.CH_StartMinimized = QtWidgets.QCheckBox(self.TAB_Main)
        self.CH_StartMinimized.setGeometry(QtCore.QRect(20, 50, 230, 17))
        self.CH_StartMinimized.setText("Start minimized")
        self.CH_StartMinimized.setToolTip("The app will start minimized")

        # Enable logging
        self.CH_EnableLogging = QtWidgets.QCheckBox(self.TAB_Main)
        self.CH_EnableLogging.setGeometry(QtCore.QRect(20, 80, 230, 17))
        self.CH_EnableLogging.setText("Enable logging")
        self.CH_EnableLogging.setToolTip(f"App logs will be saved into a text file")

        # Show player winrate and notes
        self.CH_ShowPlayerWinrates = QtWidgets.QCheckBox(self.TAB_Main)
        self.CH_ShowPlayerWinrates.setGeometry(QtCore.QRect(20, 110, 230, 17))
        self.CH_ShowPlayerWinrates.setText("Show player winrates and notes")
        self.CH_ShowPlayerWinrates.setToolTip("The number of games and winrate you had with your ally will be shown when a game starts.\nPlayer note will show as well if specified.")

        # Duration
        self.SP_Duration = QtWidgets.QSpinBox(self.TAB_Main)
        self.SP_Duration.setGeometry(QtCore.QRect(250, 20, 42, 22))

        self.LA_Duration = QtWidgets.QLabel(self.TAB_Main)
        self.LA_Duration.setGeometry(QtCore.QRect(300, 20, 191, 21))
        self.LA_Duration.setText("Duration")
        self.LA_Duration.setToolTip("How long the overlay will show after a new game is analysed.")

        # Monitor
        self.SP_Monitor = QtWidgets.QSpinBox(self.TAB_Main)
        self.SP_Monitor.setGeometry(QtCore.QRect(250, 50, 42, 22))
        self.SP_Monitor.setMinimum(1)
        self.SP_Monitor.setToolTip("Determines on which monitor the overlay will be shown")

        self.LA_Monitor = QtWidgets.QLabel(self.TAB_Main)
        self.LA_Monitor.setGeometry(QtCore.QRect(300, 50, 47, 20))
        self.LA_Monitor.setText("Monitor")
        self.LA_Monitor.setToolTip("Determines on which monitor the overlay will be shown")

        # Force hidden
        self.CH_ForceHideOverlay = QtWidgets.QCheckBox(self.TAB_Main)
        self.CH_ForceHideOverlay.setGeometry(QtCore.QRect(250, 110, 300, 17))
        self.CH_ForceHideOverlay.setText("Don\'t show overlay on-screen")
        self.CH_ForceHideOverlay.setToolTip("The overlay won't show directly on your screen. You can use this setting\nfor example when it's meant to be visible only on stream. Requires restart.")

        # Replay folder
        self.LA_AccountFolder = QtWidgets.QLabel(self.TAB_Main)
        self.LA_AccountFolder.setGeometry(QtCore.QRect(520, 15, 280, 16))
        self.LA_AccountFolder.setText("Specify your StarCraft II Account folder")

        self.LA_CurrentReplayFolder = QtWidgets.QLabel(self.TAB_Main)
        self.LA_CurrentReplayFolder.setEnabled(False)
        self.LA_CurrentReplayFolder.setGeometry(QtCore.QRect(520, 25, 400, 31))

        self.BT_ChooseFolder = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_ChooseFolder.setGeometry(QtCore.QRect(520, 55, 150, 25))
        self.BT_ChooseFolder.setText('Choose folder')
        self.BT_ChooseFolder.setToolTip('Choose your account folder.\nThis is usually not necessary and the app will find its location automatically.')
        self.BT_ChooseFolder.clicked.connect(self.findReplayFolder)

        # Info label
        self.LA_InfoLabel = QtWidgets.QLabel(self.TAB_Main)
        self.LA_InfoLabel.setGeometry(QtCore.QRect(20, 560, 800, 20))

        # Apply
        self.BT_MainApply = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_MainApply.setGeometry(QtCore.QRect(867, 400, 75, 25))
        self.BT_MainApply.setText('Apply')
        self.BT_MainApply.clicked.connect(self.saveSettings)
        self.BT_MainApply.setShortcut("Enter")

        # Reset
        self.BT_MainReset = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_MainReset.setGeometry(QtCore.QRect(785, 400, 75, 25))
        self.BT_MainReset.setText('Reset')
        self.BT_MainReset.clicked.connect(self.resetSettings)
        self.BT_MainReset.setToolTip("Reset all settings apart from player notes and settings for starcraft2coop")

        ### Hotkey frame
        self.FR_HotkeyFrame = QtWidgets.QFrame(self.TAB_Main)
        self.FR_HotkeyFrame.setGeometry(QtCore.QRect(20, 170, 411, 211))
        self.FR_HotkeyFrame.setAutoFillBackground(True)
        self.FR_HotkeyFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_HotkeyFrame.setFrameShadow(QtWidgets.QFrame.Plain)

        # Label
        self.LA_Hotkeys = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_Hotkeys.setGeometry(QtCore.QRect(0, 10, 411, 20))
        self.LA_Hotkeys.setStyleSheet("font-weight: bold")
        self.LA_Hotkeys.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Hotkeys.setText("Hotkeys")

        # Show/hide
        self.LA_ShowHide = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_ShowHide.setGeometry(QtCore.QRect(20, 50, 111, 20))
        self.LA_ShowHide.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_ShowHide.setText("Show / hide")

        self.KEY_ShowHide = MUI.CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_ShowHide.setGeometry(QtCore.QRect(20, 70, 113, 20))
        self.KEY_ShowHide.setToolTip('The key for both showing and hiding the overlay')
        
        # Show
        self.LA_Show = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_Show.setGeometry(QtCore.QRect(150, 50, 111, 20))
        self.LA_Show.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Show.setText("Show only")

        self.KEY_Show = MUI.CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Show.setGeometry(QtCore.QRect(150, 70, 113, 20))
        self.KEY_Show.setToolTip('The key for just showing the overlay')

        # Hide
        self.LA_Hide = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_Hide.setGeometry(QtCore.QRect(280, 50, 111, 20))
        self.LA_Hide.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Hide.setText("Hide only")
        
        self.KEY_Hide = MUI.CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Hide.setGeometry(QtCore.QRect(280, 70, 113, 20))
        self.KEY_Hide.setToolTip('The key for just hiding the overlay')

        # Newer
        self.LA_Newer = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_Newer.setGeometry(QtCore.QRect(20, 120, 111, 20))
        self.LA_Newer.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Newer.setText("Show newer replay")

        self.KEY_Newer = MUI.CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Newer.setGeometry(QtCore.QRect(20, 140, 113, 20))
        self.KEY_Newer.setToolTip('The key for showing a newer replay than is currently displayed')

        # Older
        self.LA_Older = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_Older.setGeometry(QtCore.QRect(150, 120, 111, 20))
        self.LA_Older.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Older.setText("Show older replay")

        self.KEY_Older = MUI.CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Older.setGeometry(QtCore.QRect(150, 140, 113, 20))
        self.KEY_Older.setToolTip('The key for showing an older replay than is currently displayed')

        # Winrates
        self.LA_Winrates = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_Winrates.setGeometry(QtCore.QRect(280, 120, 111, 20))
        self.LA_Winrates.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Winrates.setText("Show player winrates")

        self.KEY_Winrates = MUI.CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Winrates.setGeometry(QtCore.QRect(280, 140, 113, 20))
        self.KEY_Winrates.setToolTip('The key for showing the last player winrates and notes')

        for item in {self.KEY_ShowHide, self.KEY_Show, self.KEY_Hide, self.KEY_Newer, self.KEY_Older, self.KEY_Winrates}:
            item.setStyleSheet("color: #444;")

        # Colors
        self.FR_CustomizeColors = QtWidgets.QFrame(self.TAB_Main)
        self.FR_CustomizeColors.setGeometry(QtCore.QRect(445, 170, 241, 211))
        self.FR_CustomizeColors.setAutoFillBackground(True)
        self.FR_CustomizeColors.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_CustomizeColors.setFrameShadow(QtWidgets.QFrame.Plain)

        # Customize colors 
        self.LA_CustomizeColors = QtWidgets.QLabel(self.FR_CustomizeColors)
        self.LA_CustomizeColors.setGeometry(QtCore.QRect(0, 10, 241, 20))
        self.LA_CustomizeColors.setStyleSheet("font-weight: bold")
        self.LA_CustomizeColors.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_CustomizeColors.setText("Customize colors")

        # Note
        self.LA_More = QtWidgets.QLabel(self.FR_CustomizeColors)
        self.LA_More.setEnabled(False)
        self.LA_More.setGeometry(QtCore.QRect(0, 19, 241, 31))
        self.LA_More.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_More.setText("more via editing custom.css")

        color_x_offset = 50
        color_height = 20
        color_width = 140

        self.LA_P1 = QtWidgets.QPushButton(self.FR_CustomizeColors)
        self.LA_P1.setGeometry(QtCore.QRect(color_x_offset, 70, color_width, color_height))
        self.LA_P1.clicked.connect(lambda: self.openColorDialog(self.LA_P1))

        self.LA_P2 = QtWidgets.QPushButton(self.FR_CustomizeColors)
        self.LA_P2.setGeometry(QtCore.QRect(color_x_offset, 100, color_width, color_height))
        self.LA_P2.clicked.connect(lambda: self.openColorDialog(self.LA_P2))

        self.LA_Amon = QtWidgets.QPushButton(self.FR_CustomizeColors)
        self.LA_Amon.setGeometry(QtCore.QRect(color_x_offset, 130, color_width, color_height))
        self.LA_Amon.clicked.connect(lambda: self.openColorDialog(self.LA_Amon))

        self.LA_Mastery = QtWidgets.QPushButton(self.FR_CustomizeColors)
        self.LA_Mastery.setGeometry(QtCore.QRect(color_x_offset, 160, color_width, color_height))
        self.LA_Mastery.clicked.connect(lambda: self.openColorDialog(self.LA_Mastery))

        # Aom
        self.FR_Aom = QtWidgets.QFrame(self.TAB_Main)
        self.FR_Aom.setGeometry(QtCore.QRect(700, 170, 241, 211))
        self.FR_Aom.setAutoFillBackground(True)
        self.FR_Aom.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_Aom.setFrameShadow(QtWidgets.QFrame.Plain)

        self.LA_AomPage = QtWidgets.QLabel(self.FR_Aom)
        self.LA_AomPage.setGeometry(QtCore.QRect(0, 10, 241, 20))
        self.LA_AomPage.setStyleSheet("font-weight: bold")
        self.LA_AomPage.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_AomPage.setText("Settings for starcraft2coop.com")

        self.ED_AomAccount = QtWidgets.QLineEdit(self.FR_Aom)
        self.ED_AomAccount.setGeometry(QtCore.QRect(62, 70, 121, 20))
        self.ED_AomAccount.setAlignment(QtCore.Qt.AlignCenter)
        self.ED_AomAccount.setPlaceholderText("account name")

        self.ED_AomSecretKey = QtWidgets.QLineEdit(self.FR_Aom)
        self.ED_AomSecretKey.setGeometry(QtCore.QRect(62, 100, 121, 20))
        self.ED_AomSecretKey.setAlignment(QtCore.Qt.AlignCenter)
        self.ED_AomSecretKey.setPlaceholderText("secret key")
        self.ED_AomSecretKey.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)

        self.BT_AomTest = QtWidgets.QPushButton(self.FR_Aom)
        self.BT_AomTest.setGeometry(QtCore.QRect(75, 160, 85, 23))
        self.BT_AomTest.clicked.connect(self.validateAOM)
        self.BT_AomTest.setText("Verify") 
        self.BT_AomTest.setToolTip("Test if the combination of the account name and the secret key is valid")

        # Version
        self.LA_Version = QtWidgets.QLabel(self.TAB_Main)
        self.LA_Version.setGeometry(QtCore.QRect(825, 560, 141, 20))
        self.LA_Version.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing)
        self.LA_Version.setText(f"The app is up to date (v{str(APPVERSION)[0]}.{str(APPVERSION)[1:]})")
        self.LA_Version.setEnabled(False)        

        ##############################
        ######### PLAYERS TAB ########
        ##############################

        self.TAB_Players = QtWidgets.QWidget()

        # Controls 
        self.FR_Winrate_Controls = QtWidgets.QFrame(self.TAB_Players)
        self.FR_Winrate_Controls.setGeometry(QtCore.QRect(0, 540, TabWidget.frameGeometry().width(), 60))
        self.FR_Winrate_Controls.setAutoFillBackground(True)
        self.FR_Winrate_Controls.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_Winrate_Controls.setFrameShadow(QtWidgets.QFrame.Raised)

        # Search
        self.ED_Winrate_Search = QtWidgets.QLineEdit(self.FR_Winrate_Controls)
        self.ED_Winrate_Search.setGeometry(QtCore.QRect(65, 12, 610, 20))
        self.ED_Winrate_Search.setAlignment(QtCore.Qt.AlignCenter)
        self.ED_Winrate_Search.setPlaceholderText("Search for player name or note")
        self.ED_Winrate_Search.textChanged.connect(self.filter_players)

        # Top 50
        self.CH_OnlyTop50 = QtWidgets.QCheckBox(self.FR_Winrate_Controls)
        self.CH_OnlyTop50.setGeometry(QtCore.QRect(700, 13, 200, 17))
        self.CH_OnlyTop50.setText("Show max 50 players")
        self.CH_OnlyTop50.setChecked(True)
        self.CH_OnlyTop50.stateChanged.connect(self.filter_players)

        # Scroll
        self.SC_PlayersScrollArea = QtWidgets.QScrollArea(self.TAB_Players)
        self.SC_PlayersScrollArea.setGeometry(QtCore.QRect(0, 0, TabWidget.frameGeometry().width()-5, TabWidget.frameGeometry().height()-70))
        self.SC_PlayersScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.SC_PlayersScrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.SC_PlayersScrollArea.setWidgetResizable(True)

        self.SC_PlayersScrollAreaContents = QtWidgets.QWidget()
        self.SC_PlayersScrollAreaContents.setGeometry(QtCore.QRect(0, 0, 961, 561))
        self.SC_PlayersScrollAreaContentsLayout = QtWidgets.QVBoxLayout()
        self.SC_PlayersScrollAreaContentsLayout.setAlignment(QtCore.Qt.AlignTop)
        self.SC_PlayersScrollAreaContentsLayout.setContentsMargins(10,0,0,0)

        # Heading
        self.WD_WinratesHeading = QtWidgets.QWidget(self.SC_PlayersScrollAreaContents)
        self.WD_WinratesHeading.setGeometry(QtCore.QRect(0, 10, 931, 31))
        self.WD_WinratesHeading.setStyleSheet("font-weight:bold")
        self.WD_WinratesHeading.setMinimumHeight(25)
        self.WD_WinratesHeading.setMaximumHeight(25) 
        self.SC_PlayersScrollAreaContentsLayout.addWidget(self.WD_WinratesHeading)

        self.LA_Name = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_Name.setGeometry(QtCore.QRect(40, 0, 41, 31))
        self.LA_Name.setText("Name")

        self.LA_Wins = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_Wins.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Wins.setGeometry(QtCore.QRect(260, 0, 50, 31))
        self.LA_Wins.setText("▼ Wins")

        self.LA_Losses = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_Losses.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Losses.setGeometry(QtCore.QRect(330, 0, 41, 31))
        self.LA_Losses.setText("Losses")

        self.LA_Winrate = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_Winrate.setGeometry(QtCore.QRect(400, 0, 51, 31))
        self.LA_Winrate.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Winrate.setText("Winrate")

        self.LA_Note = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_Note.setGeometry(QtCore.QRect(550, 0, 330, 31))
        self.LA_Note.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Note.setText("Player note (displayed together with winrates)")

        ###########################
        ######## GAMES TAB ########
        ###########################

        self.TAB_Games = QtWidgets.QWidget()

        # Scroll
        self.SC_GamesScrollArea = QtWidgets.QScrollArea(self.TAB_Games)
        self.SC_GamesScrollArea.setGeometry(QtCore.QRect(0, 0, TabWidget.frameGeometry().width()-5, TabWidget.frameGeometry().height()))
        self.SC_GamesScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.SC_GamesScrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.SC_GamesScrollArea.setWidgetResizable(True)

        self.SC_GamesScrollAreaContent = QtWidgets.QWidget()
        self.SC_GamesScrollAreaContent.setGeometry(QtCore.QRect(0, 0, 961, 561))
        self.SC_GamesScrollAreaContentLayout = QtWidgets.QVBoxLayout()
        self.SC_GamesScrollAreaContentLayout.setAlignment(QtCore.Qt.AlignTop)
        self.SC_GamesScrollAreaContentLayout.setContentsMargins(10,0,0,0)

        # Heading
        self.WD_RecentGamesHeading = QtWidgets.QWidget(self.SC_GamesScrollAreaContent)
        self.WD_RecentGamesHeading.setGeometry(QtCore.QRect(10, 10, 931, 22))
        self.WD_RecentGamesHeading.setStyleSheet("font-weight: bold")
        self.WD_RecentGamesHeading.setMinimumHeight(25)
        self.WD_RecentGamesHeading.setMaximumHeight(25) 
        self.SC_GamesScrollAreaContentLayout.addWidget(self.WD_RecentGamesHeading)

        self.LA_Difficulty = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Difficulty.setGeometry(QtCore.QRect(590, 0, 81, 31))
        self.LA_Difficulty.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Difficulty.setText("Difficulty")

        self.LA_Player2 = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Player2.setGeometry(QtCore.QRect(363, 0, 81, 31))
        self.LA_Player2.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Player2.setText("Player 2")

        self.LA_Enemy = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Enemy.setGeometry(QtCore.QRect(480, 0, 41, 31))
        self.LA_Enemy.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Enemy.setText("Enemy")

        self.LA_Length = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Length.setGeometry(QtCore.QRect(530, 0, 71, 31))
        self.LA_Length.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Length.setText("Length")

        self.LA_Map = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Map.setGeometry(QtCore.QRect(40, 0, 41, 31))
        self.LA_Map.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LA_Map.setText("Map")

        self.LA_Player1 = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Player1.setGeometry(QtCore.QRect(223, 0, 81, 31))
        self.LA_Player1.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Player1.setText("Player 1")

        self.LA_Result = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Result.setGeometry(QtCore.QRect(140, 0, 41, 31))
        self.LA_Result.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Result.setText("Result")

        self.LA_Date = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Date.setGeometry(QtCore.QRect(660, 0, 81, 31))
        self.LA_Date.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Date.setText("Date")
      
        # Finishing
        self.SC_GamesScrollAreaContent.setLayout(self.SC_GamesScrollAreaContentLayout)
        self.SC_GamesScrollArea.setWidget(self.SC_GamesScrollAreaContent)

        ###########################
        ######## STATS TAB ########
        ###########################

        self.TAB_Stats = QtWidgets.QWidget()
        self.FR_Stats = QtWidgets.QFrame(self.TAB_Stats)
        self.FR_Stats.setGeometry(QtCore.QRect(10, 0, 964, 151))
        self.FR_Stats.setAutoFillBackground(False)

        # Difficulty
        self.CH_DiffCasual = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffCasual.setGeometry(QtCore.QRect(10, 20, 61, 17))
        self.CH_DiffCasual.setChecked(True)
        self.CH_DiffCasual.setText("Casual")

        self.CH_DiffNormal = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffNormal.setGeometry(QtCore.QRect(10, 40, 61, 17))
        self.CH_DiffNormal.setChecked(True)
        self.CH_DiffNormal.setText("Normal")

        self.CH_DiffHard = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffHard.setGeometry(QtCore.QRect(10, 60, 51, 17))
        self.CH_DiffHard.setChecked(True)
        self.CH_DiffHard.setText("Hard")

        self.CH_DiffBrutal = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffBrutal.setGeometry(QtCore.QRect(10, 80, 51, 17))
        self.CH_DiffBrutal.setChecked(True)
        self.CH_DiffBrutal.setText("Brutal")

        self.CH_DiffBrutalPlus = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffBrutalPlus.setGeometry(QtCore.QRect(10, 100, 61, 17))
        self.CH_DiffBrutalPlus.setChecked(True)
        self.CH_DiffBrutalPlus.setText("Brutal+")

        # Region
        self.CH_Region_NA = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Region_NA.setGeometry(QtCore.QRect(90, 20, 71, 17))
        self.CH_Region_NA.setChecked(True)
        self.CH_Region_NA.setText("Americas")

        self.CH_Region_EU = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Region_EU.setGeometry(QtCore.QRect(90, 40, 71, 17))
        self.CH_Region_EU.setChecked(True)
        self.CH_Region_EU.setText("Europe")

        self.CH_Region_KR = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Region_KR.setGeometry(QtCore.QRect(90, 60, 61, 17))
        self.CH_Region_KR.setChecked(True)
        self.CH_Region_KR.setText("Asia")

        self.CH_Region_CN = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Region_CN.setGeometry(QtCore.QRect(90, 80, 61, 17))
        self.CH_Region_CN.setChecked(True)
        self.CH_Region_CN.setText("China")

        # Type
        self.CH_TypeNormal = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_TypeNormal.setGeometry(QtCore.QRect(180, 20, 101, 17))
        self.CH_TypeNormal.setChecked(True)
        self.CH_TypeNormal.setText("Normal games")

        self.CH_TypeMutation = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_TypeMutation.setGeometry(QtCore.QRect(180, 40, 101, 17))
        self.CH_TypeMutation.setChecked(True)
        self.CH_TypeMutation.setText("Mutations")

        # Generate
        self.BT_Generate = QtWidgets.QPushButton(self.FR_Stats)
        self.BT_Generate.setGeometry(QtCore.QRect(770, 40, 171, 51))
        self.BT_Generate.setText("Generate stats")
        self.BT_Generate.setStyleSheet('font-weight: bold')
        self.BT_Generate.clicked.connect(self.generate_stats)
        self.BT_Generate.setEnabled(False)

        # Games found
        self.LA_GamesFound = QtWidgets.QLabel(self.FR_Stats)
        self.LA_GamesFound.setEnabled(False)
        self.LA_GamesFound.setGeometry(QtCore.QRect(570, 110, 381, 20))
        self.LA_GamesFound.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.LA_GamesFound.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)

        # Main names
        self.LA_IdentifiedPlayers = QtWidgets.QLabel(self.FR_Stats)
        self.LA_IdentifiedPlayers.setEnabled(False)
        self.LA_IdentifiedPlayers.setGeometry(QtCore.QRect(570, 125, 381, 20))
        self.LA_IdentifiedPlayers.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.LA_IdentifiedPlayers.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)

        # Date
        self.LA_ReplayDate = QtWidgets.QLabel(self.FR_Stats)
        self.LA_ReplayDate.setGeometry(QtCore.QRect(480, 20, 101, 16))
        self.LA_ReplayDate.setStyleSheet('font-weight: bold')
        self.LA_ReplayDate.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LA_ReplayDate.setText("Replay date")

        self.LA_To = QtWidgets.QLabel(self.FR_Stats)
        self.LA_To.setGeometry(QtCore.QRect(600, 70, 31, 16))
        self.LA_To.setText("To")
        self.TM_ToDate = QtWidgets.QDateEdit(self.FR_Stats)
        self.TM_ToDate.setGeometry(QtCore.QRect(480, 70, 110, 22))
        self.TM_ToDate.setDateTime(QtCore.QDateTime(QtCore.QDate(2030, 12, 30), QtCore.QTime(0, 0, 0)))
        self.TM_ToDate.setDisplayFormat("d/M/yyyy")

        self.LA_From = QtWidgets.QLabel(self.FR_Stats)
        self.LA_From.setGeometry(QtCore.QRect(600, 40, 31, 16))
        self.LA_From.setText("From")
        self.TM_FromDate = QtWidgets.QDateEdit(self.FR_Stats)
        self.TM_FromDate.setGeometry(QtCore.QRect(480, 40, 110, 22))
        self.TM_FromDate.setDateTime(QtCore.QDateTime(QtCore.QDate(2015, 11, 10), QtCore.QTime(0, 0, 0)))
        self.TM_FromDate.setDisplayFormat("d/M/yyyy")

        # Game length
        self.LA_GameLength = QtWidgets.QLabel(self.FR_Stats)
        self.LA_GameLength.setGeometry(QtCore.QRect(310, 20, 131, 16))
        self.LA_GameLength.setStyleSheet('font-weight: bold')
        self.LA_GameLength.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LA_GameLength.setText("Game length (minutes)")

        self.LA_Maximum = QtWidgets.QLabel(self.FR_Stats)
        self.LA_Maximum.setGeometry(QtCore.QRect(360, 70, 51, 16))
        self.LA_Maximum.setText("Maximum")

        self.LA_Minimum = QtWidgets.QLabel(self.FR_Stats)
        self.LA_Minimum.setGeometry(QtCore.QRect(360, 40, 41, 16))
        self.LA_Minimum.setText("Minimum")

        self.SP_MaxGamelength = QtWidgets.QSpinBox(self.FR_Stats)
        self.SP_MaxGamelength.setGeometry(QtCore.QRect(310, 70, 42, 22))
        self.SP_MaxGamelength.setMinimum(0)
        self.SP_MaxGamelength.setMaximum(1000)
        self.SP_MaxGamelength.setProperty("value", 0)

        self.SP_MinGamelength = QtWidgets.QSpinBox(self.FR_Stats)
        self.SP_MinGamelength.setGeometry(QtCore.QRect(310, 40, 42, 22))
        self.SP_MinGamelength.setMaximum(1000)
        self.SP_MinGamelength.setProperty("value", 0)



        ##### RESULTS #####
        self.TABW_StatResults = QtWidgets.QTabWidget(self.TAB_Stats)
        self.TABW_StatResults.setGeometry(QtCore.QRect(5, 126, 971, 451))
        self.TABW_StatResults.setAccessibleDescription("")
        self.TABW_StatResults.setObjectName("TABW_StatResults")
        self.TAB_FastestsMaps = QtWidgets.QWidget()
        self.TAB_FastestsMaps.setObjectName("TAB_FastestsMaps")
        self.FR_Fastest_VT = QtWidgets.QFrame(self.TAB_FastestsMaps)
        self.FR_Fastest_VT.setGeometry(QtCore.QRect(10, 20, 741, 381))
        self.FR_Fastest_VT.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_Fastest_VT.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FR_Fastest_VT.setObjectName("FR_Fastest_VT")
        self.LA_Fastest_Map_VT = QtWidgets.QLabel(self.FR_Fastest_VT)
        self.LA_Fastest_Map_VT.setGeometry(QtCore.QRect(10, 10, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.LA_Fastest_Map_VT.setFont(font)
        self.LA_Fastest_Map_VT.setObjectName("LA_Fastest_Map_VT")
        self.LA_Fastest_P1_VT = QtWidgets.QLabel(self.FR_Fastest_VT)
        self.LA_Fastest_P1_VT.setGeometry(QtCore.QRect(10, 40, 171, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.LA_Fastest_P1_VT.setFont(font)
        self.LA_Fastest_P1_VT.setObjectName("LA_Fastest_P1_VT")
        self.LA_Fastest_P2_VT = QtWidgets.QLabel(self.FR_Fastest_VT)
        self.LA_Fastest_P2_VT.setGeometry(QtCore.QRect(240, 40, 201, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.LA_Fastest_P2_VT.setFont(font)
        self.LA_Fastest_P2_VT.setObjectName("LA_Fastest_P2_VT")
        self.LA_Fastest_P1Mastery_VT = QtWidgets.QLabel(self.FR_Fastest_VT)
        self.LA_Fastest_P1Mastery_VT.setGeometry(QtCore.QRect(10, 80, 171, 91))
        self.LA_Fastest_P1Mastery_VT.setObjectName("LA_Fastest_P1Mastery_VT")
        self.LA_Fastest_TimeRace_VT = QtWidgets.QLabel(self.FR_Fastest_VT)
        self.LA_Fastest_TimeRace_VT.setGeometry(QtCore.QRect(160, 10, 111, 20))
        self.LA_Fastest_TimeRace_VT.setObjectName("LA_Fastest_TimeRace_VT")
        self.LA_Fastest_P2Mastery_VT = QtWidgets.QLabel(self.FR_Fastest_VT)
        self.LA_Fastest_P2Mastery_VT.setGeometry(QtCore.QRect(240, 80, 171, 91))
        self.LA_Fastest_P2Mastery_VT.setObjectName("LA_Fastest_P2Mastery_VT")
        self.BT_FastestMap_Show = QtWidgets.QPushButton(self.TAB_FastestsMaps)
        self.BT_FastestMap_Show.setGeometry(QtCore.QRect(670, 380, 81, 23))
        self.BT_FastestMap_Show.setStyleSheet("")
        self.BT_FastestMap_Show.setObjectName("BT_FastestMap_Show")
        self.BT_FastestMap_Find = QtWidgets.QPushButton(self.TAB_FastestsMaps)
        self.BT_FastestMap_Find.setGeometry(QtCore.QRect(590, 380, 75, 23))
        self.BT_FastestMap_Find.setStyleSheet("")
        self.BT_FastestMap_Find.setObjectName("BT_FastestMap_Find")
        self.GB_FastestMapOverview = QtWidgets.QGroupBox(self.TAB_FastestsMaps)
        self.GB_FastestMapOverview.setGeometry(QtCore.QRect(760, 10, 191, 391))
        self.GB_FastestMapOverview.setObjectName("GB_FastestMapOverview")
        self.BT_Fastest_VT = QtWidgets.QPushButton(self.GB_FastestMapOverview)
        self.BT_Fastest_VT.setGeometry(QtCore.QRect(10, 15, 171, 20))
        self.BT_Fastest_VT.setObjectName("BT_Fastest_VT")


        self.BT_Fastest_CoA = QtWidgets.QPushButton(self.GB_FastestMapOverview)
        self.BT_Fastest_CoA.setGeometry(QtCore.QRect(10, 35, 171, 20))
        self.BT_Fastest_CoA.setObjectName("BT_Fastest_CoA")
        self.BT_Fastest_MO = QtWidgets.QPushButton(self.GB_FastestMapOverview)
        self.BT_Fastest_MO.setGeometry(QtCore.QRect(10, 55, 171, 20))
        self.BT_Fastest_MO.setObjectName("BT_Fastest_MO")
        self.BT_Fastest_VP = QtWidgets.QPushButton(self.GB_FastestMapOverview)
        self.BT_Fastest_VP.setGeometry(QtCore.QRect(10, 75, 171, 20))
        self.BT_Fastest_VP.setObjectName("BT_Fastest_VP")
        self.TABW_StatResults.addTab(self.TAB_FastestsMaps, "")
        self.TAB_Maps = QtWidgets.QWidget()
        self.TAB_Maps.setObjectName("TAB_Maps")
        self.TBD_Maps = QtWidgets.QLabel(self.TAB_Maps)
        self.TBD_Maps.setGeometry(QtCore.QRect(20, 10, 221, 21))
        self.TBD_Maps.setObjectName("TBD_Maps")
        self.TABW_StatResults.addTab(self.TAB_Maps, "")
        self.TAB_MyCommanders = QtWidgets.QWidget()
        self.TAB_MyCommanders.setObjectName("TAB_MyCommanders")
        self.TBD_MyCommanders = QtWidgets.QLabel(self.TAB_MyCommanders)
        self.TBD_MyCommanders.setGeometry(QtCore.QRect(10, 10, 311, 21))
        self.TBD_MyCommanders.setObjectName("TBD_MyCommanders")
        self.TABW_StatResults.addTab(self.TAB_MyCommanders, "")
        self.TAB_AlliedCommanders = QtWidgets.QWidget()
        self.TAB_AlliedCommanders.setObjectName("TAB_AlliedCommanders")
        self.TBD_AlliedCommanders = QtWidgets.QLabel(self.TAB_AlliedCommanders)
        self.TBD_AlliedCommanders.setGeometry(QtCore.QRect(10, 10, 421, 21))
        self.TBD_AlliedCommanders.setObjectName("TBD_AlliedCommanders")
        self.TABW_StatResults.addTab(self.TAB_AlliedCommanders, "")
        self.TAB_Difficulty = QtWidgets.QWidget()
        self.TAB_Difficulty.setObjectName("TAB_Difficulty")
        self.TBD_Difficulty = QtWidgets.QLabel(self.TAB_Difficulty)
        self.TBD_Difficulty.setGeometry(QtCore.QRect(10, 10, 191, 21))
        self.TBD_Difficulty.setObjectName("TBD_Difficulty")
        self.TABW_StatResults.addTab(self.TAB_Difficulty, "")
        self.TAB_ProgressionRegions = QtWidgets.QWidget()
        self.TAB_ProgressionRegions.setObjectName("TAB_ProgressionRegions")
        self.TBD_ProgressionRegions = QtWidgets.QLabel(self.TAB_ProgressionRegions)
        self.TBD_ProgressionRegions.setGeometry(QtCore.QRect(10, 10, 321, 31))
        self.TBD_ProgressionRegions.setObjectName("TBD_ProgressionRegions")
        self.TABW_StatResults.addTab(self.TAB_ProgressionRegions, "")


        self.LA_Fastest_Map_VT.setText("Void Thrashing")
        self.LA_Fastest_P1_VT.setText("Maguro (Tychus)\n"
"Legendary Outlaw (P0)")
        self.LA_Fastest_P2_VT.setText("KingDime (Mengsk)\n"
"Emperor of the Dominion (P0)")
        self.LA_Fastest_P1Mastery_VT.setText("30 sfdsf0 nsdfdf\n"
"15 sfdsfdsfdsf\n"
"30 sdfdsff\n"
"15 sdfdsfd\n"
"0 sdfdsfdf\n"
"30 sdfdsfd")
        self.LA_Fastest_TimeRace_VT.setText("11:24, Terran")
        self.LA_Fastest_P2Mastery_VT.setText("30 sfdsf0 nsdfdf\n"
"15 sfdsfdsfdsf\n"
"30 sdfdsff\n"
"15 sdfdsfd\n"
"0 sdfdsfdf\n"
"30 sdfdsfd")
        self.BT_FastestMap_Show.setText("Show overlay")
        self.BT_FastestMap_Find.setText("Find file")
        self.GB_FastestMapOverview.setTitle("Overview")
        self.BT_Fastest_VT.setText("12:03 - Void Thrashing")
        self.BT_Fastest_CoA.setText("18:56 - Chain of Ascension")
        self.BT_Fastest_MO.setText("20:28 -  Mist Opportunities")
        self.BT_Fastest_VP.setText("22:54 - The Vermillion Problem")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_FastestsMaps), "Fastest maps")
        self.TBD_Maps.setText("Map freq, winrate, avg victory time")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_Maps), "Maps")
        self.TBD_MyCommanders.setText("Commander games, freq, winrate, median APM")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_MyCommanders), "My commanders")
        self.TBD_AlliedCommanders.setText("Frequency (corrected), typical ally mastery, prestige frequency, median apm")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_AlliedCommanders), "Allied commanders")
        self.TBD_Difficulty.setText("Games and winrate per difficulty")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_Difficulty), "Difficulty")
        self.TBD_ProgressionRegions.setText("# games, winrate per region, max ascension\n"
"Per commander prestige played at lvl 14-15")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_ProgressionRegions), "Progression and regions")


        ###########################
        ######## LINKS TAB ########
        ###########################

        self.TAB_Links = QtWidgets.QWidget()

        # Links
        self.FR_Links = QtWidgets.QFrame(self.TAB_Links)
        self.FR_Links.setGeometry(QtCore.QRect(20, 20, 471, 191))
        self.FR_Links.setAutoFillBackground(True)
        self.FR_Links.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_Links.setFrameShadow(QtWidgets.QFrame.Plain)

        # GitHub
        self.IMG_GitHub = QtWidgets.QLabel(self.FR_Links)
        self.IMG_GitHub.setGeometry(QtCore.QRect(20, 20, 41, 41))
        self.IMG_GitHub.setPixmap(QtGui.QPixmap(innerPath("src/github.png")))

        self.LA_GitHub = QtWidgets.QLabel(self.FR_Links)
        self.LA_GitHub.setGeometry(QtCore.QRect(70, 20, 131, 41))
        self.LA_GitHub.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LA_GitHub.setText('<a href="https://github.com/FluffyMaguro/SC2_Coop_overlay">GitHub</a>')

        # Maguro.one
        self.IMG_MaguroOne = QtWidgets.QLabel(self.FR_Links)
        self.IMG_MaguroOne.setGeometry(QtCore.QRect(20, 70, 31, 41))
        self.IMG_MaguroOne.setPixmap(QtGui.QPixmap(innerPath("src/maguro.jpg")))

        self.LA_MaguroOne = QtWidgets.QLabel(self.FR_Links)
        self.LA_MaguroOne.setGeometry(QtCore.QRect(70, 70, 131, 41))
        self.LA_MaguroOne.setText('<a href="www.maguro.one">Maguro.one</a>')

        # Twitter
        self.IMG_Twitter = QtWidgets.QLabel(self.FR_Links)
        self.IMG_Twitter.setGeometry(QtCore.QRect(20, 120, 41, 51))
        self.IMG_Twitter.setPixmap(QtGui.QPixmap(innerPath("src/twitter.png")))

        self.LA_Twitter = QtWidgets.QLabel(self.FR_Links)
        self.LA_Twitter.setGeometry(QtCore.QRect(70, 130, 131, 31))
        self.LA_Twitter.setText('<a href="https://twitter.com/FluffyMaguro">Twitter</a>')

        # Subreddit
        self.IMG_Reddit = QtWidgets.QLabel(self.FR_Links)
        self.IMG_Reddit.setGeometry(QtCore.QRect(240, 10, 41, 51))
        self.IMG_Reddit.setPixmap(QtGui.QPixmap(innerPath("src/reddit.png")))

        self.LA_Subreddit = QtWidgets.QLabel(self.FR_Links)
        self.LA_Subreddit.setGeometry(QtCore.QRect(290, 20, 161, 31))
        self.LA_Subreddit.setText('<a href="https://www.reddit.com/r/starcraft2coop/">Co-op subreddit</a>')

        # Forums
        self.IMG_BattleNet = QtWidgets.QLabel(self.FR_Links)
        self.IMG_BattleNet.setGeometry(QtCore.QRect(240, 60, 41, 51))
        self.IMG_BattleNet.setPixmap(QtGui.QPixmap(innerPath("src/sc2.png")))

        self.LA_BattleNet = QtWidgets.QLabel(self.FR_Links)
        self.LA_BattleNet.setGeometry(QtCore.QRect(290, 70, 141, 31))
        self.LA_BattleNet.setText('<a href="https://us.forums.blizzard.com/en/sc2/c/co-op-missions-discussion">Co-op forums</a>')

        # Discord
        self.IMG_Discord = QtWidgets.QLabel(self.FR_Links)
        self.IMG_Discord.setGeometry(QtCore.QRect(240, 120, 31, 41))
        self.IMG_Discord.setPixmap(QtGui.QPixmap(innerPath("src/discord.png")))
        
        self.LA_Discord = QtWidgets.QLabel(self.FR_Links)
        self.LA_Discord.setGeometry(QtCore.QRect(290, 120, 141, 41))
        self.LA_Discord.setText('<a href="https://discord.gg/VQnXMdm">Co-op discord</a>')

        # Donate
        self.FR_Donate = QtWidgets.QFrame(self.TAB_Links)
        self.FR_Donate.setGeometry(QtCore.QRect(20, 225, 471, 100))
        self.FR_Donate.setAutoFillBackground(True)
        self.FR_Donate.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_Donate.setFrameShadow(QtWidgets.QFrame.Plain)

        self.IMG_Donate = QtWidgets.QLabel(self.FR_Donate)
        self.IMG_Donate.setGeometry(QtCore.QRect(170, 14, 200, 41))
        self.IMG_Donate.setPixmap(QtGui.QPixmap(innerPath("src/paypal.png")))

        self.LA_Donate = QtWidgets.QLabel(self.FR_Donate)
        self.LA_Donate.setGeometry(QtCore.QRect(130, 47, 250, 41))
        self.LA_Donate.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LA_Donate.setText('<a href="https://www.paypal.com/paypalme/FluffyMaguro">donate if you feel generous</a>')

        # Styling
        for item in {self.LA_MaguroOne, self.LA_Subreddit, self.LA_Twitter, self.LA_GitHub, self.LA_Discord, self.LA_BattleNet, self.LA_Donate}:
            item.setStyleSheet("font-size: 18px")
            item.setOpenExternalLinks(True)


        ############################
        ####### FINALIZATION #######
        ############################

        TabWidget.addTab(self.TAB_Main, "")
        TabWidget.setTabText(TabWidget.indexOf(self.TAB_Main), "Settings")

        TabWidget.addTab(self.TAB_Games, "")
        TabWidget.setTabText(TabWidget.indexOf(self.TAB_Games), "Games")

        TabWidget.addTab(self.TAB_Players, "")
        TabWidget.setTabText(TabWidget.indexOf(self.TAB_Players), "Players")

        TabWidget.addTab(self.TAB_Stats, "")
        TabWidget.setTabText(TabWidget.indexOf(self.TAB_Stats), "Stats")

        TabWidget.addTab(self.TAB_Links, "")
        TabWidget.setTabText(TabWidget.indexOf(self.TAB_Links), "Links")

        TabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(TabWidget)

        if not HF.isWindows():
            self.CH_StartWithWindows.setChecked(False)
            self.CH_StartWithWindows.setEnabled(False)


    def loadSettings(self):
        """ Loads settings from the config file if there is any, updates UI elements accordingly"""
        self.downloading = False

        self.default_settings = {
            'start_with_windows':False,
            'start_minimized':False,
            'enable_logging':False,
            'show_player_winrates':True,
            'duration':60,
            'monitor':1,
            'force_hide_overlay':False,  
            'account_folder':None,                  
            'hotkey_show/hide':'Ctrl+*',
            'hotkey_show':None,
            'hotkey_hide':None,
            'hotkey_newer':'Alt+/',
            'hotkey_older':'Alt+*',
            'hotkey_winrates':'Ctrl+Alt+-',
            'color_player1':'#0080F8',
            'color_player2':'#00D532',
            'color_amon':'#FF0000',
            'color_mastery':'#FFDC87',
            'aom_account':None,
            'aom_secret_key':None,
            'player_notes':dict(),
            'list_games': 100
            }

        self.settings = self.default_settings.copy()

        # Try to load base config if there is one         
        try:         
            if os.path.isfile(SETTING_FILE):
                with open(SETTING_FILE, 'r') as f:
                    self.settings = json.load(f)
            else:
                with open(SETTING_FILE, 'w') as f:
                    json.dump(self.settings, f, indent=2)
        except:
            logger.error(f'Error while loading settings:\n{traceback.format_exc()}')

        # Make sure all keys are here
        for key in self.default_settings:
            if key not in self.settings:
                self.settings[key] = self.default_settings[key]

        # Check if account directory valid, update if not
        self.settings['account_folder'] = HF.get_account_dir(self.settings['account_folder'])

        # Delete install bat if it's there
        if os.path.isfile(truePath('install.bat')):
            os.remove(truePath('install.bat'))

        self.updateUI()
        self.check_for_updates()

        # Show TabWidget or not
        TabWidget.settings = self.settings

        if self.settings['start_minimized']:
            TabWidget.hide()
            TabWidget.show_minimize_message()
        else:
            TabWidget.show()

        # Check write permissions
        self.write_permissions = HF.write_permission_granted()
        if not self.write_permissions:
            self.sendInfoMessage('Permission denied. Add an exception to your anti-virus for this folder. Sorry', color='red')

        logclass.LOGGING = self.settings['enable_logging'] if self.write_permissions else False

        self.manage_keyboard_threads()


    def check_for_updates(self):
        """ Checks for updates and changes UI accordingly"""
        self.new_version = HF.new_version(APPVERSION)

        if not self.new_version:
            return

        self.LA_Version.setText('New version available!')

        # Create button
        self.BT_NewUpdate = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_NewUpdate.setGeometry(QtCore.QRect(20, 400, 157, 40))
        self.BT_NewUpdate.setText('Download update')
        self.BT_NewUpdate.setStyleSheet('font-weight: bold;')
        self.BT_NewUpdate.clicked.connect(self.start_download)

        # Check if it's already downloaded
        save_path = truePath(f'Updates\\{self.new_version.split("/")[-1]}')

        if not HF.isWindows():
            self.sendInfoMessage('Update available', color='green')
            return

        if os.path.isfile(save_path):
            self.update_is_ready_for_install()
        else:
            self.PB_download = QtWidgets.QProgressBar(self.TAB_Main) 
            self.PB_download.setGeometry(21, 569, 830, 10) 
            self.PB_download.hide()


    def start_download(self):
        """ Starts downloading an update"""
        if self.downloading:
            return

        self.downloading = True
        self.BT_NewUpdate.setText('Downloading')
        self.BT_NewUpdate.setEnabled(False)
        self.BT_NewUpdate.clicked.disconnect()
        self.PB_download.show()

        if not os.path.isdir(truePath('Updates')):
            os.mkdir(truePath('Updates'))

        save_path = truePath(f'Updates\\{self.new_version.split("/")[-1]}')
        urllib.request.urlretrieve(self.new_version, save_path, self.download_progress_bar_updater) 


    def download_progress_bar_updater(self, blocknum, blocksize, totalsize):
        """ Updates the progress bar accordingly"""
        readed_data = blocknum * blocksize 

        if totalsize > 0: 
            download_percentage = readed_data * 100 / totalsize 
            self.PB_download.setValue(int(download_percentage)) 
            QtWidgets.QApplication.processEvents() 

            if download_percentage >= 100:
                self.update_is_ready_for_install()
                self.downloading = False


    def update_is_ready_for_install(self):
        """ Changes button text and connect it to another function"""
        self.BT_NewUpdate.setText('Restart and update')
        self.BT_NewUpdate.setEnabled(True)
        try:
            self.BT_NewUpdate.clicked.disconnect()    
        except:
            pass
        self.BT_NewUpdate.clicked.connect(self.install_update)


    def install_update(self):
        """ Starts the installation """
        archive = truePath(f'Updates\\{self.new_version.split("/")[-1]}')
        where_to_extract = truePath('Updates\\New')
        app_folder = truePath('')

        # Check if it's corrupt
        if HF.archive_is_corrupt(archive):
            os.remove(archive)
            self.sendInfoMessage('Archive corrupt. Removing file.', color='red')

            self.BT_NewUpdate.clicked.disconnect()
            self.BT_NewUpdate.clicked.connect(self.start_download)
            self.BT_NewUpdate.setText('Download update')
            return

        # Delete previously extracted archive
        if os.path.isdir(where_to_extract):
            shutil.rmtree(where_to_extract)

        # Extract archive
        HF.extract_archive(archive, where_to_extract)

        # Create and run install.bat file
        installfile = truePath('install.bat')
        with open(installfile,'w') as f:
            f.write(f'@echo off\necho Installation will start shortly...\ntimeout /t 5 /nobreak > NUL\nrobocopy "{where_to_extract}" "{os.path.abspath(app_folder)}" /E\ntimeout /t 2 /nobreak > NUL\nrmdir /s /q "{truePath("Updates")}"\n"{truePath("SCO.exe")}"')

        self.saveSettings()
        os.startfile(installfile)
        app.quit()


    def updateUI(self):
        """ Update UI elements based on the current settings """
        self.CH_StartWithWindows.setChecked(self.settings['start_with_windows'])
        self.CH_StartMinimized.setChecked(self.settings['start_minimized'])
        self.CH_EnableLogging.setChecked(self.settings['enable_logging'])
        self.CH_ShowPlayerWinrates.setChecked(self.settings['show_player_winrates'])
        self.CH_ForceHideOverlay.setChecked(self.settings['force_hide_overlay'])
        self.SP_Duration.setProperty("value", self.settings['duration'])
        self.SP_Monitor.setProperty("value", self.settings['monitor'])
        self.LA_CurrentReplayFolder.setText(self.settings['account_folder'])

        self.KEY_ShowHide.setKeySequence(QtGui.QKeySequence.fromString(self.settings['hotkey_show/hide']))
        self.KEY_Show.setKeySequence(QtGui.QKeySequence.fromString(self.settings['hotkey_show']))
        self.KEY_Hide.setKeySequence(QtGui.QKeySequence.fromString(self.settings['hotkey_hide']))
        self.KEY_Newer.setKeySequence(QtGui.QKeySequence.fromString(self.settings['hotkey_newer']))
        self.KEY_Older.setKeySequence(QtGui.QKeySequence.fromString(self.settings['hotkey_older']))
        self.KEY_Winrates.setKeySequence(QtGui.QKeySequence.fromString(self.settings['hotkey_winrates']))

        self.ED_AomAccount.setText(self.settings['aom_account'])
        self.ED_AomSecretKey.setText(self.settings['aom_secret_key'])

        self.LA_P1.setText(f"Player 1 | {self.settings['color_player1']}")
        self.LA_P1.setStyleSheet(f"background-color: {self.settings['color_player1']}")
        self.LA_P2.setText(f"Player 2 | {self.settings['color_player2']}")
        self.LA_P2.setStyleSheet(f"background-color: {self.settings['color_player2']}")
        self.LA_Amon.setText(f"  Amon | {self.settings['color_amon']}")
        self.LA_Amon.setStyleSheet(f"background-color: {self.settings['color_amon']}")
        self.LA_Mastery.setText(f"Mastery | {self.settings['color_mastery']}")
        self.LA_Mastery.setStyleSheet(f"background-color: {self.settings['color_mastery']}")


    def saveSettings(self):
        """ Saves main settings in the settings file. """
        previous_settings = self.settings.copy()

        self.save_playernotes_to_settings()

        self.settings['start_with_windows'] = self.CH_StartWithWindows.isChecked()
        self.settings['start_minimized'] = self.CH_StartMinimized.isChecked()
        self.settings['enable_logging'] = self.CH_EnableLogging.isChecked()
        self.settings['show_player_winrates'] = self.CH_ShowPlayerWinrates.isChecked()
        self.settings['force_hide_overlay'] = self.CH_ForceHideOverlay.isChecked()
        self.settings['duration'] = self.SP_Duration.value()
        self.settings['monitor'] = self.SP_Monitor.value()

        self.settings['hotkey_show/hide'] = self.KEY_ShowHide.keySequence().toString()
        self.settings['hotkey_show'] = self.KEY_Show.keySequence().toString()
        self.settings['hotkey_hide'] = self.KEY_Hide.keySequence().toString()
        self.settings['hotkey_newer'] = self.KEY_Newer.keySequence().toString()
        self.settings['hotkey_older'] = self.KEY_Older.keySequence().toString()
        self.settings['hotkey_winrates'] = self.KEY_Winrates.keySequence().toString()

        self.settings['aom_account'] = self.ED_AomAccount.text()
        self.settings['aom_secret_key'] = self.ED_AomSecretKey.text()

        # Save settings
        try:
            with open(SETTING_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info('Settings saved')
        except:
            logger.error(f'Error while saving settings\n{traceback.format_exc()}')

        # Warning
        self.sendInfoMessage('')

        hotkeys = [self.settings['hotkey_show/hide'], self.settings['hotkey_show'], self.settings['hotkey_hide'], self.settings['hotkey_newer'], self.settings['hotkey_older'], self.settings['hotkey_winrates']]
        hotkeys = [h for h in hotkeys if not h in {None,''}]
        if len(hotkeys) > len(set(hotkeys)):
            self.sendInfoMessage('Warning: Overlapping hotkeys!', color='red')

        # Registry
        out = HF.add_to_startup(self.settings['start_with_windows'])
        if out != None:
            self.sendInfoMessage(f'Warning: {out}', color='red')
            self.settings['start_with_windows'] = False
            self.CH_StartWithWindows.setChecked(self.settings['start_with_windows'])

        # Logging
        logclass.LOGGING = self.settings['enable_logging'] if self.write_permissions else False

        # Update TabWidget for notification
        TabWidget.settings = self.settings

        # Update settings for other threads
        MF.update_settings(self.settings)

        # Compare
        changed_keys = set()
        for key in previous_settings:
            if previous_settings[key] != self.settings[key] and not (previous_settings[key] == None and self.settings[key] == ''):
                logger.info(f'Changed: {key}: {previous_settings[key]} → {self.settings[key]}')
                changed_keys.add(key)

        # Resend init message if duration has changed. Colors are handle in color picker.
        if 'duration' in changed_keys:
            MF.resend_init_message()

        # Monitor update
        if 'monitor' in changed_keys and hasattr(self, 'WebView'):
            self.set_WebView_size_location(self.settings['monitor'])

        # Update keyboard threads
        self.manage_keyboard_threads(previous_settings=previous_settings)

        
    def manage_keyboard_threads(self, previous_settings=None):
        """ Compares previous settings with current ones, and restarts keyboard threads if necessary.
        if `previous_settings` == None, then init hotkeys instead """
        hotkey_func_dict = {'hotkey_show/hide': MF.keyboard_SHOWHIDE, 'hotkey_show': MF.keyboard_SHOW, 'hotkey_hide': MF.keyboard_HIDE, 'hotkey_newer': MF.keyboard_NEWER, 'hotkey_older': MF.keyboard_OLDER, 'hotkey_winrates': MF.keyboard_PLAYERWINRATES}
        
        # Init
        if previous_settings == None:
            self.hotkey_hotkey_dict = dict()
            for key in hotkey_func_dict:
                if not self.settings[key] in {None,''}:
                    try:
                        self.hotkey_hotkey_dict[key] = keyboard.add_hotkey(self.settings[key], hotkey_func_dict[key])
                    except:
                        logger.error(traceback.format_exc())
                        self.sendInfoMessage('Failed to initialize this hotkey! Try a different one.', color='red')
        # Update
        else:
            for key in hotkey_func_dict:
                # Update current value if the hotkey changed
                if previous_settings[key] != self.settings[key] and not self.settings[key] in {None,''}:
                    if key in self.hotkey_hotkey_dict:
                        keyboard.remove_hotkey(self.hotkey_hotkey_dict[key])
                    self.hotkey_hotkey_dict[key] = keyboard.add_hotkey(self.settings[key], hotkey_func_dict[key])
                    logger.info(f'Changed hotkey of {key} to {self.settings[key]}')

                # Remove current hotkey no value
                elif self.settings[key] in {None,''} and key in self.hotkey_hotkey_dict:
                    keyboard.remove_hotkey(self.hotkey_hotkey_dict[key])
                    logger.info(f'Removing hotkey of {key}')


    def resetSettings(self):
        """ Resets settings to default values and updates UI """
        previous_settings = self.settings.copy()
        self.settings = self.default_settings.copy()
        self.settings['account_folder'] = HF.get_account_dir(path=self.settings['account_folder'])
        self.settings['aom_account'] = self.ED_AomAccount.text()
        self.settings['aom_secret_key'] = self.ED_AomSecretKey.text()
        self.settings['player_notes'] = previous_settings['player_notes']   
        self.updateUI()
        self.saveSettings()
        self.sendInfoMessage('All settings have been reset!')
        MF.update_settings(self.settings)
        MF.resend_init_message()
        self.manage_keyboard_threads(previous_settings=previous_settings)


    def findReplayFolder(self):
        """ Finds and sets account folder """
        dialog = QtWidgets.QFileDialog()
        if not self.settings['account_folder'] in {None,''}:
            dialog.setDirectory(self.settings['account_folder'])
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        if dialog.exec_():
            folder = dialog.selectedFiles()[0]
            if 'StarCraft' in folder and '/Accounts' in folder:
                logger.info(f'Changing accountdir to {folder}')
                self.settings['account_folder'] = folder
                self.LA_CurrentReplayFolder.setText(folder)
                self.sendInfoMessage(f'Account folder set succesfully! ({folder})',color='green')
                MF.update_names_and_handles(folder)
                self.CAnalysis.update_accountdir(folder)
            else:
                self.sendInfoMessage('Invalid account folder!', color='red')


    def sendInfoMessage(self, message, color='#555'):
        """ Sends info message. `color` specifies message color"""
        self.LA_InfoLabel.setText(message)
        self.LA_InfoLabel.setStyleSheet(f'color: {color}')

    
    def validateAOM(self):
        """ Validates if name/key combination is valid """
        key = self.ED_AomSecretKey.text()
        account = self.ED_AomAccount.text()

        if key != '' and account != '':
            response = HF.validate_aom_account_key(account, key)

            if 'Success' in response:
                self.sendInfoMessage(response, color='green')
            else:
                self.sendInfoMessage(response, color='red')
        else:
            self.sendInfoMessage('Fill your account name and secret key first!')


    def openColorDialog(self, button):
        """ Color picker. After the color is picked, color is saved into settings, and button updated (text and color) """
        button_dict = {self.LA_P1:'Player 1', self.LA_P2:'Player 2', self.LA_Amon:'  Amon', self.LA_Mastery:'Mastery'}
        settings_dict = {self.LA_P1:'color_player1', self.LA_P2:'color_player2', self.LA_Amon:'color_amon', self.LA_Mastery:'color_mastery'}

        color = QtWidgets.QColorDialog.getColor()

        if color.isValid():
            button.setText(f"{button_dict.get(button,'')} | {color.name()}")
            button.setStyleSheet(f'background-color: {color.name()};')
            self.settings[settings_dict[button]] = color.name()
            MF.update_settings(self.settings)
            MF.resend_init_message()


    def start_main_functionality(self):
        """ Doing the main work of looking for replays, analysing, etc. """
        logger.info(f'>>> Starting!\n{self.settings}')


        # Load overlay
        if not os.path.isfile(truePath('Layouts/Layout.html')):
            self.sendInfoMessage("Error! Failed to locate the html file", color='red')
            logger.error("Error! Failed to locate the html file")

        elif self.settings['force_hide_overlay'] or not self.write_permissions:
            logger.info(f"Not showing overlay on-screen. Force hidden: {self.settings['force_hide_overlay']} | Permissions granted: {self.write_permissions}")

        else:
            self.WebView = MUI.CustomWebView()
            self.WebView.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowTransparentForInput|QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.CoverWindow)
            self.WebView.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

            self.WebPage = self.WebView.page()
            self.WebPage.setBackgroundColor(QtCore.Qt.transparent)
            self.set_WebView_size_location(self.settings['monitor'])

            self.WebView.load(QtCore.QUrl().fromLocalFile(truePath('Layouts/Layout.html')))
            self.WebView.show()


        # Pass current settings
        MF.update_settings(self.settings)

        self.thread_server = threading.Thread(target=MF.server_thread, daemon=True)
        self.thread_server.start()

        # Using PyQt threadpool to get back results from winrate and other analysis
        self.threadpool = QtCore.QThreadPool()
        thread_init = MUI.Worker(MF.initialize_names_handles_winrates)
        thread_init.signals.result.connect(self.initialization_of_players_winrates_finished)
        self.threadpool.start(thread_init)


    def set_WebView_size_location(self, monitor):
        """ Set correct size and width for the widget. Setting it to full shows black screen on my machine, works fine on notebook (thus -1 offset) """
        sg = QtWidgets.QDesktopWidget().screenGeometry(int(monitor-1))
        try:
            self.WebView.setFixedSize(int(sg.width()*0.5 - 1), int(sg.height()))
            self.WebView.move(int(sg.width()*0.5 + 1), sg.top())
            logger.info(f'Using monitor {int(monitor)} ({sg.width()}x{sg.height()})')
        except:
            logger.errror(f"Failed to set to monitor {monitor}\n{traceback.format_exc()}")         


    def initialization_of_players_winrates_finished(self, winrate_data):
        """ What happens after we initialized player names, handles and winrates"""

        # Create player winrates UI
        self.player_winrate_UI_dict = dict()
        for idx, player in enumerate(winrate_data):
            self.player_winrate_UI_dict[player] = MUI.PlayerEntry(player, winrate_data[player][0], winrate_data[player][1], self.settings['player_notes'].get(player,None), self.SC_PlayersScrollAreaContents)
            self.SC_PlayersScrollAreaContentsLayout.addWidget(self.player_winrate_UI_dict[player].widget)
            
            if idx > 50:
                self.player_winrate_UI_dict[player].hide()

        self.SC_PlayersScrollAreaContents.setLayout(self.SC_PlayersScrollAreaContentsLayout)
        self.SC_PlayersScrollArea.setWidget(self.SC_PlayersScrollAreaContents)

        # Check for new replays
        thread_replays = MUI.Worker(MF.check_replays)
        thread_replays.signals.result.connect(self.check_replays_finished)
        self.threadpool.start(thread_replays)

        # Start mass replay analysis
        thread_mass_analysis = MUI.Worker(MR.mass_replay_analysis_thread, self.settings['account_folder'])
        thread_mass_analysis.signals.result.connect(self.mass_analysis_finished)
        self.threadpool.start(thread_mass_analysis)
        logger.info('Starting mass replay analysis')
        
        # Show player winrates
        if self.settings['show_player_winrates']:
            thread_check_for_newgame = MUI.Worker(MR.check_for_new_game)
            self.threadpool.start(thread_check_for_newgame)


    def check_replays_finished(self, replay_dict):
        """ Launches function again. Adds game to game tab. Updates player winrate data. """

        # Launch thread anew
        thread_replays = MUI.Worker(MF.check_replays)
        thread_replays.signals.result.connect(self.check_replays_finished)
        self.threadpool.start(thread_replays)
        
        # Add game to game tab
        if hasattr(self, 'CAnalysis'):
            self.game_UI_dict[replay_dict['file']] = MUI.GameEntry(replay_dict, self.CAnalysis.main_handles, self.SC_GamesScrollAreaContent)
            self.SC_GamesScrollAreaContentLayout.insertWidget(1, self.game_UI_dict[replay_dict['file']].widget)     

        # Update player winrate data
        new_players = {replay_dict['players'][1]['name'], replay_dict['players'][2]['name']}
        for player in self.player_winrate_UI_dict:
            if player in new_players and player in MF.player_winrate_data:
                self.player_winrate_UI_dict[player].update_winrates(MF.player_winrate_data[player])
                new_players.remove(player)

        # Create new player entry if necessary
        if len(new_players) > 0:
            for player in new_players:
                if player in MF.player_winrate_data:
                    self.player_winrate_UI_dict[player] = MUI.PlayerEntry(player, MF.player_winrate_data[player][0], MF.player_winrate_data[player][1], self.settings['player_notes'].get(player,None), self.SC_PlayersScrollAreaContents)
                    self.SC_PlayersScrollAreaContentsLayout.addWidget(self.player_winrate_UI_dict[player].widget)

        # Update mass replay analysis
        if hasattr(self, 'CAnalysis'):
            self.CAnalysis.add_parsed_replay(replay_dict)


    def save_playernotes_to_settings(self):
        """ Saves player notes from UI to settings dict"""
        for player in self.player_winrate_UI_dict:
            if not self.player_winrate_UI_dict[player].get_note() in {None,''}:
                self.settings['player_notes'][player] = self.player_winrate_UI_dict[player].get_note()
            elif player in self.settings['player_notes']:
                del self.settings['player_notes'][player] 


    def filter_players(self):
        """ Filters only players with string in name or note """
        text = self.ED_Winrate_Search.text().lower()
        idx = 0
        for player in self.player_winrate_UI_dict:
            note = self.player_winrate_UI_dict[player].get_note().lower()

            if self.CH_OnlyTop50.isChecked() and idx >= 50:
                self.player_winrate_UI_dict[player].hide()

            elif text in player.lower() or text in note or ('note' in text and not note in {None,''}):
                self.player_winrate_UI_dict[player].show()
                idx += 1
            else:
                self.player_winrate_UI_dict[player].hide()


    def mass_analysis_finished(self, result):
        self.CAnalysis = result

        # Add games to games tab
        self.game_UI_dict = dict()
        for game in self.CAnalysis.get_last_replays(self.settings['list_games']):
            self.game_UI_dict[game['file']] = MUI.GameEntry(game, self.CAnalysis.main_handles, self.SC_GamesScrollAreaContent)
            self.SC_GamesScrollAreaContentLayout.addWidget(self.game_UI_dict[game['file']].widget)            

        # Update stats tab
        player_names = (', ').join(self.CAnalysis.main_names)
        self.LA_IdentifiedPlayers.setText(f"Main players: {player_names}")
        self.LA_GamesFound.setText(f"Games found: {len(self.CAnalysis.ReplayData)}")
        self.BT_Generate.setEnabled(True)
      

    def generate_stats(self):
        """ Generate stats and passes data to be shown"""

        if not hasattr(self, 'CAnalysis'):
            logger.error('Mass analysis hasn\'t finished yet')
            return

        # Filter
        include_mutations = True if self.CH_TypeMutation.isChecked() else False
        include_normal_games = True if self.CH_TypeNormal.isChecked() else False

        difficulty_filter = set()
        if not self.CH_DiffCasual.isChecked():
            difficulty_filter.add('Casual')
        if not self.CH_DiffNormal.isChecked():
            difficulty_filter.add('Normal')
        if not self.CH_DiffHard.isChecked():
            difficulty_filter.add('Hard')
        if not self.CH_DiffBrutal.isChecked():
            difficulty_filter.add('Brutal')
        if not self.CH_DiffBrutalPlus.isChecked():
            difficulty_filter = difficulty_filter.union({1,2,3,4,5,6})

        region_filter = set()
        if not self.CH_Region_NA.isChecked():
            region_filter.add('NA')
        if not self.CH_Region_EU.isChecked():
            region_filter.add('EU')
        if not self.CH_Region_KR.isChecked():
            region_filter.add('KR')
        if not self.CH_Region_CN.isChecked():
            region_filter.add('CN')

        mindate = self.TM_FromDate.date().toPyDate().strftime('%Y%m%d%H%M%S')
        mindate = None if mindate == '20151110000000' else int(mindate)
        maxdate = self.TM_ToDate.date().toPyDate().strftime('%Y%m%d%H%M%S')
        maxdate = None if maxdate == '20301230000000' else int(maxdate)

        minlength = None if self.SP_MinGamelength.value() == 0 else self.SP_MinGamelength.value()
        maxLength = None if self.SP_MaxGamelength.value() == 0 else self.SP_MaxGamelength.value()

        # Analyse
        analysis = self.CAnalysis.analyse_replays(
                                  include_mutations=include_mutations, 
                                  include_normal_games=include_normal_games, 
                                  difficulty_filter=difficulty_filter, 
                                  region_filter=region_filter, 
                                  mindate=mindate, 
                                  maxdate=maxdate, 
                                  minlength=minlength, 
                                  maxLength=maxLength)
        
        self.LA_GamesFound.setText(f"Games found: {analysis['games']}")


        # !!! update results
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    TabWidget = QtWidgets.QTabWidget()
    TabWidget = MUI.CustomQTabWidget()

    ui = UI_TabWidget()
    ui.setupUI(TabWidget)
    ui.loadSettings()
    ui.start_main_functionality()

    # Do stuff before the app is closed
    exit_event = app.exec_()
    MF.stop_threads()
    ui.saveSettings()
    TabWidget.tray_icon.hide()
    sys.exit(exit_event)
