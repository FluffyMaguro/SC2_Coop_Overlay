"""
Main module for StarCraft II Co-op Overlay

Causal chain:
Setup -> Load Settings -> UI
                       -> Server manager (thread)
                       -> Twitch bot (thread)
                       -> Initialize winrates & names -> Check replays (loop of threads)
                                                      -> Player winrates (thread)
                                                      -> Mass replay analysis -> Generate stats
"""
import os
import sys
import json
import shutil
import threading
import traceback
import urllib.request
from functools import partial
from datetime import datetime

import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets

import SCOFunctions.MUserInterface as MUI
import SCOFunctions.MainFunctions as MF
import SCOFunctions.HelperFunctions as HF
import SCOFunctions.MassReplayAnalysis as MR
from SCOFunctions.MRandomizer import randomize
from SCOFunctions.MLogging import logclass
from SCOFunctions.MFilePath import truePath, innerPath
from SCOFunctions.MTwitchBot import TwitchBot
from SCOFunctions.SC2Dictionaries import prestige_names, CommanderMastery


logger = logclass('SCO','INFO')
logclass.FILE = truePath("Logs.txt")

APPVERSION = 191
SETTING_FILE = truePath('Settings.json')


class UI_TabWidget(object):
    def setupUI(self, TabWidget):
        TabWidget.setWindowTitle(f"StarCraft Co-op Overlay (v{str(APPVERSION)[0]}.{str(APPVERSION)[1:]})")
        TabWidget.setWindowIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        TabWidget.setFixedSize(980, 610)
        TabWidget.tray_icon.setToolTip(f'StarCraft Co-op Overlay (v{str(APPVERSION)[0]}.{str(APPVERSION)[1:]})')

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
        self.CH_ShowPlayerWinrates.setToolTip("The number of games and winrate you had with your ally will be shown when a game starts.\nPlayer note will show as well if specified. Requires restart to enable.")

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
        self.CH_ForceHideOverlay.setToolTip("The overlay won't show directly on your screen. You can use this setting\nfor example when it's meant to be visible only on stream.")

        # Replay folder
        self.LA_AccountFolder = QtWidgets.QLabel(self.TAB_Main)
        self.LA_AccountFolder.setGeometry(QtCore.QRect(520, 15, 350, 16))
        self.LA_AccountFolder.setText("Change locations of StarCraft II account folder and screenshot folder")

        self.BT_ChooseFolder = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_ChooseFolder.setGeometry(QtCore.QRect(520, 36, 150, 25))
        self.BT_ChooseFolder.setText('Account folder')
        self.BT_ChooseFolder.setToolTip('Choose your account folder.\nThis is usually not necessary and the app will find its location automatically.')
        self.BT_ChooseFolder.clicked.connect(self.findReplayFolder)

        self.LA_CurrentReplayFolder = QtWidgets.QLabel(self.TAB_Main)
        self.LA_CurrentReplayFolder.setEnabled(False)
        self.LA_CurrentReplayFolder.setGeometry(QtCore.QRect(520, 53, 400, 31))

        # Screenshot folder
        self.BT_ScreenshotLocation = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_ScreenshotLocation.setGeometry(QtCore.QRect(520, 90, 150, 25))
        self.BT_ScreenshotLocation.setText('Screenshot folder')
        self.BT_ScreenshotLocation.setToolTip('Choose the folder where screenshots are saved')
        self.BT_ScreenshotLocation.clicked.connect(self.chooseScreenshotFolder)

        self.LA_ScreenshotLocation = QtWidgets.QLabel(self.TAB_Main)
        self.LA_ScreenshotLocation.setEnabled(False)
        self.LA_ScreenshotLocation.setGeometry(QtCore.QRect(520, 108, 400, 31))

        # Info label
        self.LA_InfoLabel = QtWidgets.QLabel(self.TAB_Main)
        self.LA_InfoLabel.setGeometry(QtCore.QRect(20, 560, 800, 20))

        # Apply
        self.BT_MainApply = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_MainApply.setGeometry(QtCore.QRect(867, 400, 75, 25))
        self.BT_MainApply.setText('Apply')
        self.BT_MainApply.clicked.connect(self.saveSettings)
        self.BT_MainApply.setShortcut("Enter")

        # Debug
        self.BT_MainDebug = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_MainDebug.setGeometry(QtCore.QRect(867, 430, 75, 25))
        self.BT_MainDebug.setText('Debug')
        self.BT_MainDebug.clicked.connect(self.debug_function)
        self.BT_MainDebug.hide()

        # Reset
        self.BT_MainReset = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_MainReset.setGeometry(QtCore.QRect(785, 400, 75, 25))
        self.BT_MainReset.setText('Reset')
        self.BT_MainReset.clicked.connect(self.resetSettings)
        self.BT_MainReset.setToolTip("Reset all settings apart from player notes, settings for starcraft2coop and the twitch bot")

        # Screenshot
        self.BT_Screenshot = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_Screenshot.setGeometry(QtCore.QRect(19, 400, 157, 40))
        self.BT_Screenshot.setText('Overlay screenshot')
        self.BT_Screenshot.setToolTip('Take screenshot of the overlay and save it on your desktop or chosen location')
        self.BT_Screenshot.clicked.connect(self.save_screenshot)

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
        self.BT_AomTest.setGeometry(QtCore.QRect(75, 160, 85, 25))
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
        self.LA_Losses.setGeometry(QtCore.QRect(328, 0, 45, 31))
        self.LA_Losses.setText("Losses")

        self.LA_Winrate = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_Winrate.setGeometry(QtCore.QRect(400, 0, 51, 31))
        self.LA_Winrate.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Winrate.setText("Winrate")

        self.LA_Note = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_Note.setGeometry(QtCore.QRect(550, 0, 330, 31))
        self.LA_Note.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Note.setText("Player note (displayed together with winrates)")

        # Wait
        self.LA_Winrates_Wait = QtWidgets.QLabel(self.TAB_Players)
        self.LA_Winrates_Wait.setGeometry(QtCore.QRect(0, 0, self.SC_PlayersScrollAreaContents.width(), self.SC_PlayersScrollAreaContents.height()))
        self.LA_Winrates_Wait.setText('<b>Please wait. This can take few minutes the first time.<br>Analyzing your replays.</b>')
        self.LA_Winrates_Wait.setAlignment(QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)


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

        self.LA_Games_Wait = QtWidgets.QLabel(self.SC_GamesScrollAreaContent)
        self.LA_Games_Wait.setGeometry(QtCore.QRect(0, 0, self.SC_GamesScrollAreaContent.width(), self.SC_GamesScrollAreaContent.height()))
        self.LA_Games_Wait.setText('<b>Please wait. This can take few minutes the first time.<br>Analyzing your replays.</b>')
        self.LA_Games_Wait.setAlignment(QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)

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
        self.LA_Enemy.setGeometry(QtCore.QRect(478, 0, 44, 31))
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
        self.LA_Result.setGeometry(QtCore.QRect(145, 0, 41, 31))
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

        # Difficulty
        self.CH_DiffCasual = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffCasual.setGeometry(QtCore.QRect(10, 20, 70, 17))
        self.CH_DiffCasual.setChecked(True)
        self.CH_DiffCasual.setText("Casual")
        self.CH_DiffCasual.stateChanged.connect(self.generate_stats)

        self.CH_DiffNormal = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffNormal.setGeometry(QtCore.QRect(10, 40, 70, 17))
        self.CH_DiffNormal.setChecked(True)
        self.CH_DiffNormal.setText("Normal")
        self.CH_DiffNormal.stateChanged.connect(self.generate_stats)

        self.CH_DiffHard = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffHard.setGeometry(QtCore.QRect(10, 60, 70, 17))
        self.CH_DiffHard.setChecked(True)
        self.CH_DiffHard.setText("Hard")
        self.CH_DiffHard.stateChanged.connect(self.generate_stats)

        self.CH_DiffBrutal = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffBrutal.setGeometry(QtCore.QRect(10, 80, 70, 17))
        self.CH_DiffBrutal.setChecked(True)
        self.CH_DiffBrutal.setText("Brutal")
        self.CH_DiffBrutal.stateChanged.connect(self.generate_stats)

        self.CH_DiffBrutalPlus = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffBrutalPlus.setGeometry(QtCore.QRect(10, 100, 70, 17))
        self.CH_DiffBrutalPlus.setChecked(True)
        self.CH_DiffBrutalPlus.setText("Brutal+")
        self.CH_DiffBrutalPlus.stateChanged.connect(self.generate_stats)

        # Region
        self.CH_Region_NA = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Region_NA.setGeometry(QtCore.QRect(90, 20, 71, 17))
        self.CH_Region_NA.setChecked(True)
        self.CH_Region_NA.setText("Americas")
        self.CH_Region_NA.stateChanged.connect(self.generate_stats)

        self.CH_Region_EU = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Region_EU.setGeometry(QtCore.QRect(90, 40, 71, 17))
        self.CH_Region_EU.setChecked(True)
        self.CH_Region_EU.setText("Europe")
        self.CH_Region_EU.stateChanged.connect(self.generate_stats)

        self.CH_Region_KR = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Region_KR.setGeometry(QtCore.QRect(90, 60, 61, 17))
        self.CH_Region_KR.setChecked(True)
        self.CH_Region_KR.setText("Asia")
        self.CH_Region_KR.stateChanged.connect(self.generate_stats)

        self.CH_Region_CN = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Region_CN.setGeometry(QtCore.QRect(90, 80, 61, 17))
        self.CH_Region_CN.setChecked(True)
        self.CH_Region_CN.setText("China")
        self.CH_Region_CN.stateChanged.connect(self.generate_stats)

        # Type
        self.CH_TypeNormal = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_TypeNormal.setGeometry(QtCore.QRect(180, 20, 110, 17))
        self.CH_TypeNormal.setChecked(True)
        self.CH_TypeNormal.setText("Normal games")
        self.CH_TypeNormal.stateChanged.connect(self.generate_stats)

        self.CH_TypeMutation = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_TypeMutation.setGeometry(QtCore.QRect(180, 40, 110, 17))
        self.CH_TypeMutation.setChecked(True)
        self.CH_TypeMutation.setText("Mutations")
        self.CH_TypeMutation.stateChanged.connect(self.generate_stats)

        # Sub15 and both mains
        self.CH_Sub15 = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Sub15.setGeometry(QtCore.QRect(290, 40, 150, 17))
        self.CH_Sub15.setChecked(True)
        self.CH_Sub15.setText("Include levels 1-14")
        self.CH_Sub15.setToolTip("Include games where the main player was level 1-14")
        self.CH_Sub15.stateChanged.connect(self.generate_stats)

        self.CH_Over15 = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Over15.setGeometry(QtCore.QRect(290, 60, 150, 17))
        self.CH_Over15.setChecked(True)
        self.CH_Over15.setText("Include levels 15+")
        self.CH_Over15.setToolTip("Include games where the main player was level 15+")
        self.CH_Over15.stateChanged.connect(self.generate_stats)

        self.CH_DualMain = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DualMain.setGeometry(QtCore.QRect(290, 20, 250, 17))
        self.CH_DualMain.setChecked(False)
        self.CH_DualMain.setText("Include multi-box games")
        self.CH_DualMain.setToolTip("Include games where both players belong to your accounts")
        self.CH_DualMain.stateChanged.connect(self.generate_stats)

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

        # Date time frame
        self.FR_DateTime = QtWidgets.QFrame(self.FR_Stats)
        self.FR_DateTime.setGeometry(QtCore.QRect(470, 15, 500, 300))

        # Date
        self.LA_ReplayDate = QtWidgets.QLabel(self.FR_DateTime)
        self.LA_ReplayDate.setGeometry(QtCore.QRect(160, 0, 101, 16))
        self.LA_ReplayDate.setStyleSheet('font-weight: bold')
        self.LA_ReplayDate.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LA_ReplayDate.setText("Replay date")

        self.LA_To = QtWidgets.QLabel(self.FR_DateTime)
        self.LA_To.setGeometry(QtCore.QRect(280, 52, 31, 16))
        self.LA_To.setText("To")
        self.TM_ToDate = QtWidgets.QDateEdit(self.FR_DateTime)
        self.TM_ToDate.setGeometry(QtCore.QRect(160, 52, 110, 22))
        self.TM_ToDate.setDateTime(QtCore.QDateTime(QtCore.QDate(2030, 12, 30), QtCore.QTime(0, 0, 0)))
        self.TM_ToDate.setDisplayFormat("d/M/yyyy")
        self.TM_ToDate.dateChanged.connect(self.generate_stats)

        self.LA_From = QtWidgets.QLabel(self.FR_DateTime)
        self.LA_From.setGeometry(QtCore.QRect(280, 22, 31, 16))
        self.LA_From.setText("From")
        self.TM_FromDate = QtWidgets.QDateEdit(self.FR_DateTime)
        self.TM_FromDate.setGeometry(QtCore.QRect(160, 22, 110, 22))
        self.TM_FromDate.setDateTime(QtCore.QDateTime(QtCore.QDate(2015, 11, 10), QtCore.QTime(0, 0, 0)))
        self.TM_FromDate.setDisplayFormat("d/M/yyyy")
        self.TM_FromDate.dateChanged.connect(self.generate_stats)

        # Game length
        self.LA_GameLength = QtWidgets.QLabel(self.FR_DateTime)
        self.LA_GameLength.setGeometry(QtCore.QRect(0, 0, 150, 16))
        self.LA_GameLength.setStyleSheet('font-weight: bold')
        self.LA_GameLength.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LA_GameLength.setText("Game length (minutes)")

        self.LA_Maximum = QtWidgets.QLabel(self.FR_DateTime)
        self.LA_Maximum.setGeometry(QtCore.QRect(50, 52, 60, 16))
        self.LA_Maximum.setText("Maximum")

        self.LA_Minimum = QtWidgets.QLabel(self.FR_DateTime)
        self.LA_Minimum.setGeometry(QtCore.QRect(50, 22, 60, 16))
        self.LA_Minimum.setText("Minimum")

        self.SP_MaxGamelength = QtWidgets.QSpinBox(self.FR_DateTime)
        self.SP_MaxGamelength.setGeometry(QtCore.QRect(0, 52, 42, 22))
        self.SP_MaxGamelength.setMinimum(0)
        self.SP_MaxGamelength.setMaximum(1000)
        self.SP_MaxGamelength.setProperty("value", 0)
        self.SP_MaxGamelength.valueChanged.connect(self.generate_stats)

        self.SP_MinGamelength = QtWidgets.QSpinBox(self.FR_DateTime)
        self.SP_MinGamelength.setGeometry(QtCore.QRect(0, 22, 42, 22))
        self.SP_MinGamelength.setMaximum(1000)
        self.SP_MinGamelength.setProperty("value", 0)
        self.SP_MinGamelength.valueChanged.connect(self.generate_stats)

        ##### RESULTS #####
        self.TABW_StatResults = QtWidgets.QTabWidget(self.TAB_Stats)
        self.TABW_StatResults.setGeometry(QtCore.QRect(5, 126, 971, 451))

        ### TAB Maps
        self.TAB_Maps = QtWidgets.QWidget()
        self.GB_MapsOverview = QtWidgets.QFrame(self.TAB_Maps)
        self.GB_MapsOverview.setGeometry(QtCore.QRect(8, 8, 460, 420))
        self.WD_Heading = MUI.MapEntry(self.GB_MapsOverview, 0, 'Map name', 'Fastest', '▼Average', 'Wins', 'Losses', bold=True, button=False)
        self.QB_FastestMap = MUI.FastestMap(self.TAB_Maps)

        self.LA_Stats_Wait = QtWidgets.QLabel(self.TAB_Maps)
        self.LA_Stats_Wait.setGeometry(QtCore.QRect(0, 0, 470, self.TAB_Maps.height()))
        self.LA_Stats_Wait.setText('<b>Please wait. This can take few minutes the first time.<br>Analyzing your replays.</b>')
        self.LA_Stats_Wait.setAlignment(QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)

        ### TAB Difficulty & Regions
        self.TAB_DifficultyRegions = QtWidgets.QWidget()
        self.LA_Difficulty_header = MUI.DifficultyEntry('Difficuly', 'Wins', 'Losses', 'Winrate', 50, 0, bold=True, line=True, parent=self.TAB_DifficultyRegions)
        self.ProgressionStatsHeading = MUI.RegionStats('Region', {'Defeat':'Losses', 'Victory': 'Wins', 'frequency': 'Frequency','max_asc': 'Ascension level','max_com': 'Maxed commanders','winrate': 'Winrate',  'prestiges': 'Prestiges tried'}, 0, parent=self.TAB_DifficultyRegions, bold=True, line=True)

        ### TAB Commanders
        self.TAB_MyCommanders = QtWidgets.QWidget()
        self.MyCommanderHeading = MUI.MyCommanderEntry('Commander','Frequency' ,'Wins', 'Losses', 'Winrate', 'APM', 0, bold=True, line=True, parent=self.TAB_MyCommanders)
        self.MyCommanderComboBoxLabel = QtWidgets.QLabel(self.TAB_MyCommanders)
        self.MyCommanderComboBoxLabel.setGeometry(QtCore.QRect(450, 10, 100, 21))
        self.MyCommanderComboBoxLabel.setText('<b>Sort by</b>')

        self.MyCommanderComboBox = QtWidgets.QComboBox(self.TAB_MyCommanders)
        self.MyCommanderComboBox.setGeometry(QtCore.QRect(450, 30, 100, 21))
        self.MyCommanderComboBox.addItem('Frequency')
        self.MyCommanderComboBox.addItem('Wins')
        self.MyCommanderComboBox.addItem('Lossses')
        self.MyCommanderComboBox.addItem('Winrate')
        self.MyCommanderComboBox.addItem('APM')
        self.MyCommanderComboBox.activated[str].connect(self.my_commander_sort_update)

        ### TAB Allied Commanders
        self.TAB_AlliedCommanders = QtWidgets.QWidget()
        self.LA_AlliedCommanders = QtWidgets.QLabel(self.TAB_AlliedCommanders)
        self.LA_AlliedCommanders.setGeometry(QtCore.QRect(555, 408, 400, 20))
        self.LA_AlliedCommanders.setText("* Frequency has been corrected for your commander preferences")
        self.LA_AlliedCommanders.setAlignment(QtCore.Qt.AlignRight)
        self.LA_AlliedCommanders.setEnabled(False)

        self.AlliedCommanderHeading = MUI.AllyCommanderEntry('Allied commander', 'Frequency', 'Wins', 'Losses', 'Winrate', 'APM', 2, bold=True, button=False, parent=self.TAB_AlliedCommanders,)

        self.AllyCommanderComboBoxLabel = QtWidgets.QLabel(self.TAB_AlliedCommanders)
        self.AllyCommanderComboBoxLabel.setGeometry(QtCore.QRect(470, 2, 100, 21))
        self.AllyCommanderComboBoxLabel.setText('<b>Sort by</b>')

        self.AllyCommanderComboBox = QtWidgets.QComboBox(self.TAB_AlliedCommanders)
        self.AllyCommanderComboBox.setGeometry(QtCore.QRect(470, 22, 100, 21))
        self.AllyCommanderComboBox.addItem('Frequency')
        self.AllyCommanderComboBox.addItem('Wins')
        self.AllyCommanderComboBox.addItem('Lossses')
        self.AllyCommanderComboBox.addItem('Winrate')
        self.AllyCommanderComboBox.addItem('APM')
        self.AllyCommanderComboBox.activated[str].connect(self.ally_commander_sort_update)

        # Putting it together
        self.TABW_StatResults.addTab(self.TAB_Maps, "")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_Maps), "Maps")

        self.TABW_StatResults.addTab(self.TAB_AlliedCommanders, "")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_AlliedCommanders), "Allied commanders")

        self.TABW_StatResults.addTab(self.TAB_MyCommanders, "")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_MyCommanders), "My commanders")

        self.TABW_StatResults.addTab(self.TAB_DifficultyRegions, "")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_DifficultyRegions), "Difficulty and regions")

        self.TABW_StatResults.setCurrentIndex(0)

        ###########################
        ######### RNG TAB #########
        ###########################

        self.TAB_Randomizer = QtWidgets.QWidget()
        
        # Generate button
        self.BT_RNG_Generate = QtWidgets.QPushButton(self.TAB_Randomizer)
        self.BT_RNG_Generate.setGeometry(QtCore.QRect(720, 90, 150, 40))
        self.BT_RNG_Generate.setText('Generate')
        self.BT_RNG_Generate.clicked.connect(self.randomize_commander)

        # Description
        self.BT_RNG_Description = QtWidgets.QLabel(self.TAB_Randomizer)
        self.BT_RNG_Description.setGeometry(QtCore.QRect(370, 20, 510, 60))
        self.BT_RNG_Description.setWordWrap(True)
        self.BT_RNG_Description.setEnabled(False)
        self.BT_RNG_Description.setText('This commander randomizer randomly chooses a combination of commander, prestige and masteries.<br>Specify which commanders and prestiges can be picked. Mastery points will be randomized with either all points into one mastery choice, fully random or not at all.')     

        # Mastery label
        self.CB_RNG_Mastery_Label = QtWidgets.QLabel(self.TAB_Randomizer)
        self.CB_RNG_Mastery_Label.setGeometry(QtCore.QRect(370, 80, 200, 20))
        self.CB_RNG_Mastery_Label.setText('<b>Mastery</b>')

        # Mastery combo-box
        self.CB_RNG_Mastery = QtWidgets.QComboBox(self.TAB_Randomizer)
        self.CB_RNG_Mastery.setGeometry(QtCore.QRect(370, 100, 140, 21))
        self.CB_RNG_Mastery.addItem('All points into one')
        self.CB_RNG_Mastery.addItem('Fully random mastery')
        self.CB_RNG_Mastery.addItem('No mastery generated')

        # Map
        self.CB_RNG_Map = QtWidgets.QCheckBox(self.TAB_Randomizer)
        self.CB_RNG_Map.setGeometry(QtCore.QRect(530, 85, 140, 21))
        self.CB_RNG_Map.setText('Random map')

        # Race
        self.CB_RNG_Race = QtWidgets.QCheckBox(self.TAB_Randomizer)
        self.CB_RNG_Race.setGeometry(QtCore.QRect(530, 105, 140, 21))
        self.CB_RNG_Race.setText('Random enemy race')        
       
        ### Commanders & prestiges
        self.FR_RNG_GB = QtWidgets.QGroupBox(self.TAB_Randomizer)
        self.FR_RNG_GB.setGeometry(QtCore.QRect(40, 20, 280, 450))
        self.FR_RNG_GB.setTitle('Choose commanders and prestiges')

        self.FR_RNG_Commanders = QtWidgets.QFrame(self.FR_RNG_GB)
        self.FR_RNG_Commanders.setGeometry(QtCore.QRect(20, 20, 400, 400))
        self.FR_RNG_Commanders.show()

        # Heading
        self.RNG_co_heading = QtWidgets.QLabel(self.FR_RNG_Commanders)
        self.RNG_co_heading.setGeometry(QtCore.QRect(0, 5, 200, 20))
        self.RNG_co_heading.setText('<b>Commander</b>')

        self.RNG_co_heading_prestige = QtWidgets.QLabel(self.FR_RNG_Commanders)
        self.RNG_co_heading_prestige.setGeometry(QtCore.QRect(100, 5, 300, 20))
        self.RNG_co_heading_prestige.setText('<b>Prestige</b>')

        self.RNG_co_dict = dict()
        for prest in {0,1,2,3}:
            self.RNG_co_dict[('heading', prest)] = QtWidgets.QLabel(self.FR_RNG_Commanders)
            self.RNG_co_dict[('heading', prest)].setGeometry(QtCore.QRect(104+prest*30, 24, 300, 20))
            self.RNG_co_dict[('heading', prest)].setText(str(prest))

        # Fill commanders
        for idx, co in enumerate(prestige_names):
            self.RNG_co_dict[(co,'label')] = QtWidgets.QLabel(self.FR_RNG_Commanders)
            self.RNG_co_dict[(co,'label')].setGeometry(QtCore.QRect(0, 40+20*idx, 200, 20))
            self.RNG_co_dict[(co,'label')].setText(co)

            for prest in {0,1,2,3}:
                self.RNG_co_dict[(co, prest)] = QtWidgets.QCheckBox(self.FR_RNG_Commanders)
                self.RNG_co_dict[(co, prest)].setGeometry(QtCore.QRect(100+prest*30, 40+20*idx, 50, 20))
                self.RNG_co_dict[(co, prest)].setToolTip(prestige_names[co][prest])
                if prest == 0:
                    self.RNG_co_dict[(co, prest)].setChecked(True)

        ### Result
        self.FR_RNG_Result = QtWidgets.QGroupBox(self.TAB_Randomizer)
        self.FR_RNG_Result.setGeometry(QtCore.QRect(370, 150, 500, 320))
        self.FR_RNG_Result.setTitle('Result')

        # Background
        self.FR_RNG_Result_BG = QtWidgets.QLabel(self.FR_RNG_Result)
        self.FR_RNG_Result_BG.setGeometry(QtCore.QRect(0, 20, self.FR_RNG_Result.width(), 87))

        # Commander name
        self.FR_RNG_Result_CO = QtWidgets.QLabel(self.FR_RNG_Result)
        self.FR_RNG_Result_CO.setGeometry(QtCore.QRect(0, 12, self.FR_RNG_Result.width()-20, 87))
        self.FR_RNG_Result_CO.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.FR_RNG_Result_CO.setStyleSheet(f'font-weight: bold; font-size: 30px; color: white;')
        shadow = QtWidgets.QGraphicsDropShadowEffect() 
        shadow.setBlurRadius(1)
        shadow.setOffset(2)
        self.FR_RNG_Result_CO.setGraphicsEffect(shadow) 

        # Prestige
        self.FR_RNG_Result_Prestige = QtWidgets.QLabel(self.FR_RNG_Result)
        self.FR_RNG_Result_Prestige.setGeometry(QtCore.QRect(0, 35, self.FR_RNG_Result.width()-20, 87))
        self.FR_RNG_Result_Prestige.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.FR_RNG_Result_Prestige.setStyleSheet('font-size: 13px; color: white')
        self.FR_RNG_Result_Prestige.setGraphicsEffect(shadow) 

        self.FR_RNG_Result_Mastery = QtWidgets.QLabel(self.FR_RNG_Result)
        self.FR_RNG_Result_Mastery.setGeometry(QtCore.QRect(20, 90, 480, 200))
        self.FR_RNG_Result_Mastery.setStyleSheet('font-size: 13px')
        
        self.FR_RNG_Result_MapRace = QtWidgets.QLabel(self.FR_RNG_Result)
        self.FR_RNG_Result_MapRace.setGeometry(QtCore.QRect(10, 290, 480, 20))
        self.FR_RNG_Result_MapRace.setStyleSheet('font-size: 13px')
        self.FR_RNG_Result_MapRace.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignBottom)

        ############################
        ###### TWITCH BOT TAB ######
        ############################

        self.TAB_TwitchBot = QtWidgets.QWidget()

        self.qb_twitch_text = QtWidgets.QGroupBox(self.TAB_TwitchBot)
        self.qb_twitch_text.setTitle('About the twitch bot')
        self.qb_twitch_text.setGeometry(QtCore.QRect(15, 15, 550, 310 if HF.isWindows() else 555))
        
        self.la_twitch_text = QtWidgets.QLabel(self.qb_twitch_text)
        self.la_twitch_text.setWordWrap(True)
        self.la_twitch_text.setGeometry(QtCore.QRect(15, 25, 520, 500))
        self.la_twitch_text.setAlignment(QtCore.Qt.AlignTop)
        self.la_twitch_text.setOpenExternalLinks(True)
        self.la_twitch_text.setText("""This is a feature for twitch streamers. It connects the twitch chat to the StarCraft II game when playing one of my <a href="https://www.maguro.one/p/my-maps.html">MM maps</a>. 
                                    Viewers can spawn units, enemy waves, give resources, enable/disable mutators or join as a unit.<br> 
                                    <br> 
                                    This panel provides only the most basic control over the bot. To get the bot working, you have to create a new twitch account for your bot and 
                                    <a href="https://twitchapps.com/tmi/">generate oauth token</a>. Then fill in those in the Setting.json file as well as locations of your MMTwitchIntegration.SC2Banks 
                                    for different regions or accounts. See <a href="https://github.com/FluffyMaguro/SC2_Coop_overlay">read me</a> for more details. 
                                    <br><br><br>
                                    <u><b>Commands for the streamer:</b></u>
                                    <br><br>
                                    <b>!bank X</b><br> → Switches to bank X (when switching between regions or accounts)<br><br>
                                    <b>!gm full</b> | <b>!gm stop</b> | <b>!gm</b></li><br> → Sets the level to of integration to full, none, or just messages and joins (not affecting gameplay)<br><br>
                                    <b>!cooldown X</b><br>→ Sets the cooldown on commands to X seconds per viewer (default cooldown is 30s)
                                    """)

        self.bt_twitch = QtWidgets.QPushButton(self.TAB_TwitchBot)
        self.bt_twitch.setGeometry(QtCore.QRect(600, 30, 100, 25))
        self.bt_twitch.setText('Run the bot')
        self.bt_twitch.clicked.connect(self.start_stop_bot)

        self.ch_twitch = QtWidgets.QCheckBox(self.TAB_TwitchBot)
        self.ch_twitch.setGeometry(QtCore.QRect(601, 70, 200, 17))
        self.ch_twitch.setText('Start the bot automatically')

        # Info label
        self.LA_InfoTwitch = QtWidgets.QLabel(self.TAB_TwitchBot)
        self.LA_InfoTwitch.setGeometry(QtCore.QRect(20, 560, 800, 20))
        self.LA_InfoTwitch.setStyleSheet('color: red')

        ###########################
        ######## LINKS TAB ########
        ###########################

        self.TAB_Links = QtWidgets.QWidget()

        # Links
        self.FR_Links = QtWidgets.QFrame(self.TAB_Links)
        self.FR_Links.setGeometry(QtCore.QRect(20, 20, 471, 235))
        self.FR_Links.setAutoFillBackground(True)
        self.FR_Links.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_Links.setFrameShadow(QtWidgets.QFrame.Plain)

        # Maguro.one
        self.IMG_MaguroOne = QtWidgets.QLabel(self.FR_Links)
        self.IMG_MaguroOne.setGeometry(QtCore.QRect(20, 20, 31, 41))
        self.IMG_MaguroOne.setPixmap(QtGui.QPixmap(innerPath("src/maguro.jpg")))

        self.LA_MaguroOne = QtWidgets.QLabel(self.FR_Links)
        self.LA_MaguroOne.setGeometry(QtCore.QRect(70, 20, 131, 41))
        self.LA_MaguroOne.setText('<a href="www.maguro.one">Maguro.one</a>')

        # My discord
        self.IMG_MDiscord = QtWidgets.QLabel(self.FR_Links)
        self.IMG_MDiscord.setGeometry(QtCore.QRect(20, 70, 41, 51))
        self.IMG_MDiscord.setPixmap(QtGui.QPixmap(innerPath("src/mdiscord.png")))

        self.LA_MDiscord = QtWidgets.QLabel(self.FR_Links)
        self.LA_MDiscord.setGeometry(QtCore.QRect(70, 80, 131, 31))
        self.LA_MDiscord.setText('<a href="https://discord.gg/FtGdhqD">My discord</a>')

        # Twitter
        self.IMG_Twitter = QtWidgets.QLabel(self.FR_Links)
        self.IMG_Twitter.setGeometry(QtCore.QRect(20, 120, 41, 51))
        self.IMG_Twitter.setPixmap(QtGui.QPixmap(innerPath("src/twitter.png")))

        self.LA_Twitter = QtWidgets.QLabel(self.FR_Links)
        self.LA_Twitter.setGeometry(QtCore.QRect(70, 130, 160, 31))
        self.LA_Twitter.setText('<a href="https://twitter.com/FluffyMaguro">@FluffyMaguro</a>')

        # GitHub
        self.IMG_GitHub = QtWidgets.QLabel(self.FR_Links)
        self.IMG_GitHub.setGeometry(QtCore.QRect(20, 175, 41, 41))
        self.IMG_GitHub.setPixmap(QtGui.QPixmap(innerPath("src/github.png")))

        self.LA_GitHub = QtWidgets.QLabel(self.FR_Links)
        self.LA_GitHub.setGeometry(QtCore.QRect(70, 175, 200, 41))
        self.LA_GitHub.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LA_GitHub.setText('<a href="https://github.com/FluffyMaguro/SC2_Coop_overlay">Overlay on GitHub</a>')

        # Subreddit
        self.IMG_Reddit = QtWidgets.QLabel(self.FR_Links)
        self.IMG_Reddit.setGeometry(QtCore.QRect(250, 10, 41, 51))
        self.IMG_Reddit.setPixmap(QtGui.QPixmap(innerPath("src/reddit.png")))

        self.LA_Subreddit = QtWidgets.QLabel(self.FR_Links)
        self.LA_Subreddit.setGeometry(QtCore.QRect(300, 20, 161, 31))
        self.LA_Subreddit.setText('<a href="https://www.reddit.com/r/starcraft2coop/">Co-op subreddit</a>')

        # Forums
        self.IMG_BattleNet = QtWidgets.QLabel(self.FR_Links)
        self.IMG_BattleNet.setGeometry(QtCore.QRect(250, 60, 41, 51))
        self.IMG_BattleNet.setPixmap(QtGui.QPixmap(innerPath("src/sc2.png")))

        self.LA_BattleNet = QtWidgets.QLabel(self.FR_Links)
        self.LA_BattleNet.setGeometry(QtCore.QRect(300, 70, 141, 31))
        self.LA_BattleNet.setText('<a href="https://us.forums.blizzard.com/en/sc2/c/co-op-missions-discussion">Co-op forums</a>')

        # Discord
        self.IMG_Discord = QtWidgets.QLabel(self.FR_Links)
        self.IMG_Discord.setGeometry(QtCore.QRect(250, 120, 31, 41))
        self.IMG_Discord.setPixmap(QtGui.QPixmap(innerPath("src/discord.png")))
        
        self.LA_Discord = QtWidgets.QLabel(self.FR_Links)
        self.LA_Discord.setGeometry(QtCore.QRect(300, 120, 141, 41))
        self.LA_Discord.setText('<a href="https://discord.gg/VQnXMdm">Co-op discord</a>')

        # Donate
        self.FR_Donate = QtWidgets.QFrame(self.TAB_Links)
        self.FR_Donate.setGeometry(QtCore.QRect(20, 275, 471, 100))
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
        for item in {self.LA_MaguroOne, self.LA_Subreddit, self.LA_Twitter, self.LA_GitHub, self.LA_Discord, self.LA_BattleNet, self.LA_Donate, self.LA_MDiscord}:
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

        TabWidget.addTab(self.TAB_Randomizer, "")
        TabWidget.setTabText(TabWidget.indexOf(self.TAB_Randomizer), "Randomizer")

        TabWidget.addTab(self.TAB_TwitchBot, "")
        TabWidget.setTabText(TabWidget.indexOf(self.TAB_TwitchBot), "Twitch")

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
            'enable_logging':True,
            'show_player_winrates':True,
            'duration':60,
            'monitor':1,
            'force_hide_overlay':False,
            'account_folder':None,
            'screenshot_folder':None,
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
            'main_names': list(),
            'list_games': 100,
            'right_offset':0,
            'width': 0.5,
            'height':1,
            'debug_button': False,
            'rng_choices': dict(),
            'webflag': 'CoverWindow',
            'twitchbot' : {
                           'channel_name': '',
                           'bot_name': '',
                           'bot_oauth': '',
                           'bank_locations': {
                                              'Default':'',
                                              'EU':'',
                                              'NA':'',
                                              'KR':''
                                              },
                           'responses': {
                                         'commands': '!names, !syntax, !overlay, !join, !message, !mutator, !spawn, !wave, !resources',
                                         'syntax': '!spawn unit_type amount for_player (e.g. !spawn marine 10 2), !wave size tech (e.g. !wave 7 7), !resources minerals vespene for_player (e.g. !resources 1000 500 2), !mutator mutator_name (e.g. !mutator avenger), !mutator mutator_name disable, !join player (e.g. !join 2).',
                                         'overlay': 'https://github.com/FluffyMaguro/SC2_Coop_overlay',
                                         'maguro': 'www.maguro.one',
                                         'names': 'https://www.maguro.one/p/unit-names.html'
                                         },
                           'greetings': {
                                         'fluffymaguro': 'Hello Maguro!'
                                         },
                           'banned_mutators':['Vertigo', 'Propagators', 'Fatal Attraction'],
                           'banned_units':['',],                            
                           'host': 'irc.twitch.tv',
                           'port': 6667,
                           'auto_start': False,
                           }
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
            if os.path.isfile(SETTING_FILE):
                os.replace(SETTING_FILE, f'{SETTING_FILE.replace(".json","")}_corrupted.json')

        # Make sure all keys are here
        for key in self.default_settings:
            if key not in self.settings:
                self.settings[key] = self.default_settings[key]

        # Check if account directory valid, update if not
        self.settings['account_folder'] = HF.get_account_dir(self.settings['account_folder'])

        # Delete install bat if it's there
        if os.path.isfile(truePath('install.bat')):
            os.remove(truePath('install.bat'))

        # Screenshot folder
        if self.settings['screenshot_folder'] in {None,''}:
            self.settings['screenshot_folder'] = os.path.normpath(os.path.join(os.path.expanduser('~'), 'Desktop'))

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
        self.BT_NewUpdate.setGeometry(QtCore.QRect(190, 400, 157, 40))
        self.BT_NewUpdate.setText('Download update')
        self.BT_NewUpdate.setStyleSheet('font-weight: bold')
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
        self.LA_ScreenshotLocation.setText(self.settings['screenshot_folder'])

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

        self.ch_twitch.setChecked(self.settings['twitchbot']['auto_start'])
        
        if self.settings['debug_button']:
            self.BT_MainDebug.show()
        else:
            self.BT_MainDebug.hide()

        # RNG choices
        if len(self.settings['rng_choices']) > 18:
            for co in prestige_names:
                for prest in {0,1,2,3}:
                    self.RNG_co_dict[(co, prest)].setChecked(self.settings['rng_choices'][f"{co}_{prest}"])


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
        self.settings['twitchbot']['auto_start'] = self.ch_twitch.isChecked()

        # RNG choices
        for co in prestige_names:
            for prest in {0,1,2,3}:
                self.settings['rng_choices'][f"{co}_{prest}"] = self.RNG_co_dict[(co, prest)].isChecked()

        # Save settings
        try:
            with open(SETTING_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info('Settings saved')
        except:
            logger.error(f'Error while saving settings\n{traceback.format_exc()}')

        # Message
        self.sendInfoMessage('Settings applied.')

        # Warning
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

        # Show/hide overlay
        if hasattr(self, 'WebView') and self.settings['force_hide_overlay' ]and self.WebView.isVisible():
            self.WebView.hide()
        elif hasattr(self, 'WebView') and not self.settings['force_hide_overlay'] and not self.WebView.isVisible():
            self.WebView.show()

        
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
                        self.sendInfoMessage(f'Failed to initialize hotkey ({key.replace("hotkey_","")})! Try a different one.', color='red')
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
        self.settings['screenshot_folder'] = previous_settings['screenshot_folder']
        self.settings['aom_account'] = self.ED_AomAccount.text()
        self.settings['aom_secret_key'] = self.ED_AomSecretKey.text()
        self.settings['player_notes'] = previous_settings['player_notes'] 
        self.settings['twitchbot'] = previous_settings['twitchbot']
        self.updateUI()
        self.saveSettings()
        self.sendInfoMessage('All settings have been reset!')
        MF.update_settings(self.settings)
        MF.resend_init_message()
        self.manage_keyboard_threads(previous_settings=previous_settings)


    def chooseScreenshotFolder(self):
        """ Changes screenshot folder location """
        dialog = QtWidgets.QFileDialog()
        dialog.setDirectory(self.settings['screenshot_folder'])
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        if dialog.exec_():
            folder = os.path.normpath(dialog.selectedFiles()[0])
            logger.info(f'Changing screenshot_folder to {folder}')
            self.LA_ScreenshotLocation.setText(folder)
            self.settings['screenshot_folder'] = folder
            self.sendInfoMessage(f'Screenshot folder set succesfully! ({folder})',color='green')


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
                MF.update_names_and_handles(folder, MF.AllReplays)
                if hasattr(self, 'CAnalysis'):
                    self.updating_maps = QtWidgets.QWidget()
                    self.updating_maps.setWindowTitle('Adding replays')
                    self.updating_maps.setGeometry(700, 500, 300, 100)
                    self.updating_maps.setWindowIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
                    self.updating_maps_label = QtWidgets.QLabel(self.updating_maps)
                    self.updating_maps_label.setGeometry(QtCore.QRect(10, 10, 280, 80))
                    self.updating_maps_label.setText('<b>Please wait</b><br><br>You might need to restart for the game list and stats to update.')
                    self.updating_maps_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
                    self.updating_maps_label.setWordWrap(True)
                    self.updating_maps.show()
                    self.CAnalysis.update_accountdir(folder)
                    self.updating_maps.hide()

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

        else:
            self.WebView = MUI.CustomWebView()
            self.WebView.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowTransparentForInput|QtCore.Qt.WindowStaysOnTopHint|eval(f"QtCore.Qt.{self.settings['webflag']}")|QtCore.Qt.NoDropShadowWindowHint|QtCore.Qt.WindowDoesNotAcceptFocus)
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

        # Twitch both
        self.TwitchBot = TwitchBot(self.settings['twitchbot'])
        if self.settings['twitchbot']['auto_start']:
            if self.settings['twitchbot']['channel_name'] == '' or self.settings['twitchbot']['bot_name'] == '' or self.settings['twitchbot']['bot_oauth'] == '':
                logger.error(f"Invalid data for the bot\n{self.settings['twitchbot']['channel_name']=}\n{self.settings['twitchbot']['bot_name']=}\n{self.settings['twitchbot']['bot_oauth']=}")
                self.LA_InfoTwitch.setText('Twitch bot not started. Check your settings!')
            else:
                self.thread_twitch_bot = threading.Thread(target=self.TwitchBot.run_bot, daemon=True)
                self.thread_twitch_bot.start()
                self.bt_twitch.setText('Stop the bot')


    def set_WebView_size_location(self, monitor):
        """ Set correct size and width for the widget. Setting it to full shows black screen on my machine, works fine on notebook (thus -1 offset) """
        sg = QtWidgets.QDesktopWidget().screenGeometry(int(monitor-1))
        try:
            self.WebView.setFixedSize(int(sg.width()*self.settings['width']), int(sg.height()*self.settings['height']))
            self.WebView.move(int(sg.width()*(1 - self.settings['width']) + self.settings['right_offset']), sg.top())
            logger.info(f'Using monitor {int(monitor)} ({sg.width()}x{sg.height()})')
        except:
            logger.errror(f"Failed to set to monitor {monitor}\n{traceback.format_exc()}")         


    def initialization_of_players_winrates_finished(self, winrate_data):
        """ What happens after we initialized player names, handles and winrates"""

        # Create player winrates UI
        self.LA_Winrates_Wait.deleteLater()
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
            self.thread_check_for_newgame = threading.Thread(target=MF.check_for_new_game, daemon=True)
            self.thread_check_for_newgame.start()


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
        new_players = {replay_dict['players'][1]['name'], replay_dict['players'][2].get('name')}
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
        if not hasattr(self, 'player_winrate_UI_dict'):
            return
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
        self.LA_Stats_Wait.deleteLater()
        self.LA_Games_Wait.deleteLater()
        self.generate_stats()
    

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

        include_both_main = True if self.CH_DualMain.isChecked() else False
        sub_15 = True if self.CH_Sub15.isChecked() else False
        over_15 = True if self.CH_Over15.isChecked() else False

        ### Analyse
        analysis = self.CAnalysis.analyse_replays(
                                  include_mutations=include_mutations, 
                                  include_normal_games=include_normal_games, 
                                  difficulty_filter=difficulty_filter, 
                                  region_filter=region_filter, 
                                  mindate=mindate, 
                                  maxdate=maxdate, 
                                  minlength=minlength, 
                                  maxLength=maxLength,
                                  sub_15=sub_15,
                                  over_15=over_15,
                                  include_both_main=include_both_main
                                  )
        
        self.LA_GamesFound.setText(f"Games found: {analysis['games']}")


        ### Map stats

        # Delete buttons if not required
        if hasattr(self, 'stats_maps_UI_dict'):
            for item in set(self.stats_maps_UI_dict.keys()):
                self.stats_maps_UI_dict[item].deleteLater()
                del self.stats_maps_UI_dict[item]
        else:
            self.stats_maps_UI_dict = dict()

        # Sort maps
        analysis['MapData'] = {k:v for k,v in sorted(analysis['MapData'].items(), key=lambda x:x[1]['average_victory_time'])}    

        # Add map buttons & update the fastest map
        idx = 0
        for m in analysis['MapData']:
            idx += 1
            self.stats_maps_UI_dict[m] = MUI.MapEntry(self.GB_MapsOverview, idx*25, m, analysis['MapData'][m]['Fastest']['length'], analysis['MapData'][m]['average_victory_time'], analysis['MapData'][m]['Victory'], analysis['MapData'][m]['Defeat'])
            self.stats_maps_UI_dict[m].bt_button.clicked.connect(partial(self.map_link_update, mapname=m, fdict=analysis['MapData'][m]['Fastest']))

        # Try to show the last visible fastest map if it's there
        if hasattr(self, 'last_fastest_map') and self.last_fastest_map in analysis['MapData'].keys():
            self.map_link_update(self.last_fastest_map, analysis['MapData'][self.last_fastest_map]['Fastest'])

        elif len(analysis['MapData']) > 0:
            for m in analysis['MapData']:
                self.map_link_update(m, analysis['MapData'][m]['Fastest'])
                break

        # Show/hide the fastest map accordingly
        if len(analysis['MapData']) == 0:
            self.QB_FastestMap.hide()
        else:
            self.QB_FastestMap.show()


        ### Difficulty stats & region stats
        if hasattr(self, 'stats_difficulty_UI_dict'):
            for item in set(self.stats_difficulty_UI_dict.keys()):
                self.stats_difficulty_UI_dict[item].deleteLater()
                del self.stats_difficulty_UI_dict[item]
        else:
            self.stats_difficulty_UI_dict = dict()

        difficulties = ['Casual','Normal','Hard','Brutal','B+1','B+2','B+3','B+4','B+5','B+6']
        idx = 0
        AllDiff = {'Victory':0, 'Defeat':0}
        for difficulty in difficulties:
            if difficulty in analysis['DifficultyData']:
                line = True if idx+1 == len(analysis['DifficultyData']) else False
                self.stats_difficulty_UI_dict[difficulty] = MUI.DifficultyEntry(difficulty.replace('B+','Brutal+'), analysis['DifficultyData'][difficulty]['Victory'], analysis['DifficultyData'][difficulty]['Defeat'], f"{100*analysis['DifficultyData'][difficulty]['Winrate']:.0f}%", 50, idx*18+20, bg=idx%2==1, parent=self.TAB_DifficultyRegions, line=line)
                idx += 1
                AllDiff['Victory'] += analysis['DifficultyData'][difficulty]['Victory']
                AllDiff['Defeat'] += analysis['DifficultyData'][difficulty]['Defeat']

        AllDiff['Winrate'] = f"{100*AllDiff['Victory']/(AllDiff['Victory'] + AllDiff['Defeat']):.0f}%" if (AllDiff['Victory'] + AllDiff['Defeat']) > 0  else '-'
        self.stats_difficulty_UI_dict['All'] = MUI.DifficultyEntry('Σ', AllDiff['Victory'], AllDiff['Defeat'], AllDiff['Winrate'], 50, idx*18+23, parent=self.TAB_DifficultyRegions)

        # Region stats
        if hasattr(self, 'stats_region_UI_dict'):
            for item in set(self.stats_region_UI_dict.keys()):
                self.stats_region_UI_dict[item].deleteLater()
                del self.stats_region_UI_dict[item]
        else:
            self.stats_region_UI_dict = dict()

        for idx, region in enumerate(analysis['RegionData']):
            self.stats_region_UI_dict[region] = MUI.RegionStats(region, analysis['RegionData'][region], 20+idx*18, bg=True if idx%2==1 else False, parent=self.TAB_DifficultyRegions)

        ### Commander stats
        self.my_commander_analysis = analysis['CommanderData']
        self.my_commander_sort_update()

        ### Ally commander stats
        self.ally_commander_analysis = analysis['AllyCommanderData']
        self.ally_commander_sort_update()


    def my_commander_sort_update(self):
        """ Creates and updates widgets for my commander stats """
        sort_my_commanders_by = self.MyCommanderComboBox.currentText()
        translate = {'APM':'MedianAPM','Winrate':'Winrate','Lossses':'Defeat','Wins':'Victory','Frequency':'Frequency'}
        self.my_commander_analysis = {k:v for k,v in sorted(self.my_commander_analysis.items(), key=lambda x:x[1][translate[sort_my_commanders_by]], reverse=True)}

        if hasattr(self, 'stats_mycommander_UI_dict'):
            for item in set(self.stats_mycommander_UI_dict.keys()):
                self.stats_mycommander_UI_dict[item].deleteLater()
                del self.stats_mycommander_UI_dict[item]
        else:
            self.stats_mycommander_UI_dict = dict()

        idx = 0
        for co in self.my_commander_analysis:
            if co == 'any':
                continue
            line = True if idx == len(self.my_commander_analysis) - 2 else False
            self.stats_mycommander_UI_dict[co] = MUI.MyCommanderEntry(co, f"{100*self.my_commander_analysis[co]['Frequency']:.1f}%", self.my_commander_analysis[co]['Victory'], self.my_commander_analysis[co]['Defeat'], f"{100*self.my_commander_analysis[co]['Winrate']:.0f}%", f"{self.my_commander_analysis[co]['MedianAPM']:.0f}", idx*18+20, parent=self.TAB_MyCommanders, bg=True if idx%2==1 else False, line=line)
            idx += 1

        self.stats_mycommander_UI_dict['any'] = MUI.MyCommanderEntry('Σ', f"{100*self.my_commander_analysis['any']['Frequency']:.0f}%", self.my_commander_analysis['any']['Victory'], self.my_commander_analysis['any']['Defeat'], f"{100*self.my_commander_analysis['any']['Winrate']:.0f}%", f"{self.my_commander_analysis['any']['MedianAPM']:.0f}", idx*18+20, parent=self.TAB_MyCommanders)


    def ally_commander_sort_update(self):
        """ Creates and updates widgets for allu commander stats """
        sort_commanders_by = self.AllyCommanderComboBox.currentText()
        translate = {'APM':'MedianAPM','Winrate':'Winrate','Lossses':'Defeat','Wins':'Victory','Frequency':'Frequency'}
        self.ally_commander_analysis = {k:v for k,v in sorted(self.ally_commander_analysis.items(), key=lambda x:x[1][translate[sort_commanders_by]], reverse=True)}

        if hasattr(self, 'stats_allycommander_UI_dict'):
            for item in set(self.stats_allycommander_UI_dict.keys()):
                self.stats_allycommander_UI_dict[item].deleteLater()
                del self.stats_allycommander_UI_dict[item]
        else:
            self.stats_allycommander_UI_dict = dict()

        idx = 0
        spacing = 21
        firstCommander = None
        for co in self.ally_commander_analysis:
            if co == 'any':
                continue
            if firstCommander == None:
                firstCommander = co
            self.stats_allycommander_UI_dict[co] = MUI.AllyCommanderEntry(co, f"{100*self.ally_commander_analysis[co]['Frequency']:.1f}%", self.ally_commander_analysis[co]['Victory'], self.ally_commander_analysis[co]['Defeat'], f"{100*self.ally_commander_analysis[co]['Winrate']:.0f}%", f"{self.ally_commander_analysis[co]['MedianAPM']:.0f}", idx*spacing+23, parent=self.TAB_AlliedCommanders, bg=True if idx%2==1 else False)
            self.stats_allycommander_UI_dict[co].bt_button.clicked.connect(partial(self.detailed_ally_commander_stats_update, co))
            idx += 1

        self.stats_allycommander_UI_dict['any'] = MUI.AllyCommanderEntry('Σ', f"{100*self.ally_commander_analysis['any']['Frequency']:.0f}%", self.ally_commander_analysis['any']['Victory'], self.ally_commander_analysis['any']['Defeat'], f"{100*self.ally_commander_analysis['any']['Winrate']:.0f}%", f"{self.ally_commander_analysis['any']['MedianAPM']:.0f}", idx*spacing+23, parent=self.TAB_AlliedCommanders, button=False)

        # Update details
        if hasattr(self, 'ally_detailed_info') and self.ally_detailed_info != None:
            self.ally_detailed_info.deleteLater()
            self.ally_detailed_info = None

        if hasattr(self, 'ally_commander_clicked') and self.ally_commander_clicked in self.ally_commander_analysis:
            self.ally_detailed_info = MUI.AllyCommStats(self.ally_commander_clicked, self.ally_commander_analysis, parent=self.TAB_AlliedCommanders)
        elif len(self.ally_commander_analysis) > 1:
            self.ally_detailed_info = MUI.AllyCommStats(firstCommander, self.ally_commander_analysis, parent=self.TAB_AlliedCommanders)


    def detailed_ally_commander_stats_update(self, commander):
        """ Updates allied commander details"""
        self.ally_commander_clicked = commander
        if hasattr(self, 'ally_detailed_info') and self.ally_detailed_info != None:
            self.ally_detailed_info.deleteLater()
            self.ally_detailed_info = None
        self.ally_detailed_info = MUI.AllyCommStats(commander, self.ally_commander_analysis, parent=self.TAB_AlliedCommanders)


    def map_link_update(self, mapname=None, fdict=None):
        """ Updates the fastest map to clicked map """
        if len(fdict) <= 1:
            self.QB_FastestMap.hide()
        else:
            self.QB_FastestMap.update_data(mapname, fdict, self.CAnalysis.main_handles)
            self.last_fastest_map = mapname


    def save_screenshot(self):
        """ Saves screenshot of the overlay and saves it on the desktop"""
        try:
            p = QtGui.QImage(self.WebView.grab())
            height = p.height()*960/1200
            width = p.height()*650/1200
            p = p.copy(int(p.width()-width), int(p.height()*20/1200), int(width), int(height))
            p = p.convertToFormat(QtGui.QImage.Format_RGB888)

            name = f'Overlay_{datetime.now().strftime("%H%M%S")}.png'
            path = os.path.normpath(os.path.join(self.settings['screenshot_folder'], name))

            p.save(path, 'png')

            # Files smaller than 10kb consider as empty
            if os.path.getsize(path) < 10000:
                self.sendInfoMessage(f'Show overlay before taking screenshot!', color='red')
                os.remove(path)
            else:
                logger.info(f'Taking screenshot! {path}')
                self.sendInfoMessage(f'Taking screenshot! {path}', color='green')
        except:
            logger.error(traceback.format_exc())


    def start_stop_bot(self):
        """ Starts or stops the twitch bot """
        if self.settings['twitchbot']['channel_name'] == '' or self.settings['twitchbot']['bot_name'] == '' or self.settings['twitchbot']['bot_oauth'] == '':
            logger.error(f"Invalid data for the bot\n{self.settings['twitchbot']['channel_name']=}\n{self.settings['twitchbot']['bot_name']=}\n{self.settings['twitchbot']['bot_oauth']=}")
            self.LA_InfoTwitch.setText('Twitch bot not started. Check your settings!')
            return

        if not self.TwitchBot.RUNNING:
            if not hasattr(self, 'thread_twitch_bot'):
                self.thread_twitch_bot = threading.Thread(target=self.TwitchBot.run_bot, daemon=True)
                self.thread_twitch_bot.start()
            else:
                self.TwitchBot.RUNNING = True
            self.bt_twitch.setText('Stop the bot')
        else:
            self.TwitchBot.RUNNING = False
            self.bt_twitch.setText('Run the bot')


    def randomize_commander(self):
        """ Randomizes commander based on current selection """

        # Get values
        mastery_all_in = True if self.CB_RNG_Mastery.currentText() == 'All points into one' else False
        commander_dict = dict()
       
        for co in prestige_names:
            commander_dict[co] = set()
            for prest in {0,1,2,3}:
                if self.RNG_co_dict[(co, prest)].isChecked():
                    commander_dict[co].add(prest)
       
        # Randomize
        commander, prestige, mastery, mmap, race = randomize(commander_dict, mastery_all_in=mastery_all_in)

        # Update image
        self.FR_RNG_Result_BG.setStyleSheet(f'background-color: black;')
        image_file = truePath(f'Layouts/Commanders/{commander}.png')
        if os.path.isfile(image_file):
            pixmap = QtGui.QPixmap(image_file)
            pixmap = pixmap.scaled(self.FR_RNG_Result_BG.width(), self.FR_RNG_Result_BG.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
            self.FR_RNG_Result_BG.setPixmap(pixmap)

        # Commander and prestige
        self.FR_RNG_Result_CO.setText(commander)
        self.FR_RNG_Result_Prestige.setText(f"{prestige_names[commander][prestige]} (P{prestige})")

        # Mastery
        mastery = mastery if self.CB_RNG_Mastery.currentText() != 'No mastery generated' else [0,0,0,0,0,0]
        mtext = ''
        for idx, m in enumerate(CommanderMastery[commander]):
            fill = '' if mastery[idx] > 9 else '&nbsp;&nbsp;'
            style = ' style="color: #aaa"' if mastery[idx] == 0 else ''
            mtext += f"<span{style}>{fill}<b>{mastery[idx]}</b> {m}</span><br>"
        self.FR_RNG_Result_Mastery.setText(mtext)

        # Map and race
        if self.CB_RNG_Map.isChecked() and self.CB_RNG_Race.isChecked():
            self.FR_RNG_Result_MapRace.setText(f"{mmap} | {race}")
        elif self.CB_RNG_Map.isChecked():
            self.FR_RNG_Result_MapRace.setText(mmap)
        elif self.CB_RNG_Race.isChecked():
            self.FR_RNG_Result_MapRace.setText(race)
        else:
            self.FR_RNG_Result_MapRace.setText('')


    def debug_function(self):
        print('debug')
        self.settings['height'] = 0.95
        self.set_WebView_size_location(self.settings['monitor'])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    TabWidget = MUI.CustomQTabWidget()

    ui = UI_TabWidget()
    ui.setupUI(TabWidget)
    ui.loadSettings()
    ui.start_main_functionality()

    # Do stuff before the app is closed
    exit_event = app.exec_()
    TabWidget.tray_icon.hide()
    MF.stop_threads()
    ui.saveSettings()
    sys.exit(exit_event)
