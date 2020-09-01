import os
import sys
import json
import traceback

from PyQt5 import QtCore, QtGui, QtWidgets

from SCOFunctions.MLogging import logclass
from SCOFunctions.MFilePath import truePath, filePath
from SCOFunctions.MUserInterface import CustomKeySequenceEdit
from SCOFunctions.HelperFunctions import get_account_dir, validate_aom_account_key
from SCOFunctions.MainFunctions import find_names_and_handles


logger = logclass('SCO','INFO')
logclass.FILE = truePath("Logs.txt")

APPVERSION = 119
SETTING_FILE = truePath('Settings.json')


class UI_TabWidget(object):
    def setupUi(self, TabWidget):
        TabWidget.setWindowTitle(f"StarCraft Co-op Overlay ({str(APPVERSION)[0]}.{str(APPVERSION)[1:]})")
        TabWidget.setWindowIcon(QtGui.QIcon(filePath('src/OverlayIcon.ico')))
        TabWidget.setFixedSize(980, 610)
        self.TAB_Main = QtWidgets.QWidget()

        ### MAIN TAB ###

        # Start with Windows
        self.CH_StartWithWindows = QtWidgets.QCheckBox(self.TAB_Main)
        self.CH_StartWithWindows.setGeometry(QtCore.QRect(20, 20, 121, 17))
        self.CH_StartWithWindows.setText("Start with Windows")
        self.CH_StartWithWindows.setToolTip("The app will start automatically with the Windows")

        # Start minimized
        self.CH_StartMinimized = QtWidgets.QCheckBox(self.TAB_Main)
        self.CH_StartMinimized.setGeometry(QtCore.QRect(20, 50, 101, 17))
        self.CH_StartMinimized.setText("Start minimized")
        self.CH_StartMinimized.setToolTip("The app will start minimized")

        # Enable logging
        self.CH_EnableLogging = QtWidgets.QCheckBox(self.TAB_Main)
        self.CH_EnableLogging.setGeometry(QtCore.QRect(20, 80, 101, 17))
        self.CH_EnableLogging.setText("Enable logging")
        self.CH_EnableLogging.setToolTip(f"App logs will be saved into a text file")

        # Show player winrate and notes
        self.CH_ShowPlayerWinrates = QtWidgets.QCheckBox(self.TAB_Main)
        self.CH_ShowPlayerWinrates.setGeometry(QtCore.QRect(20, 110, 181, 17))
        self.CH_ShowPlayerWinrates.setText("Show player winrates and notes")
        self.CH_ShowPlayerWinrates.setToolTip("The number of games and winrate you had with your ally will be shown when a game starts.\nPlayer note will show as well if specified.")

        # Duration
        self.SP_Duration = QtWidgets.QSpinBox(self.TAB_Main)
        self.SP_Duration.setGeometry(QtCore.QRect(250, 20, 42, 22))

        self.LA_Duration = QtWidgets.QLabel(self.TAB_Main)
        self.LA_Duration.setGeometry(QtCore.QRect(300, 20, 191, 21))
        self.LA_Duration.setText("Duration for which overlay is shown")

        # Monitor
        self.SP_Monitor = QtWidgets.QSpinBox(self.TAB_Main)
        self.SP_Monitor.setGeometry(QtCore.QRect(250, 50, 42, 22))
        self.SP_Monitor.setMinimum(1)

        self.LA_Monitor = QtWidgets.QLabel(self.TAB_Main)
        self.LA_Monitor.setGeometry(QtCore.QRect(300, 50, 47, 20))
        self.LA_Monitor.setText("Monitor")
        self.LA_Monitor.setToolTip("Determines on which monitor the overlay will be shown")

        # Force hidden
        self.CH_ForceHideOverlay = QtWidgets.QCheckBox(self.TAB_Main)
        self.CH_ForceHideOverlay.setGeometry(QtCore.QRect(250, 110, 171, 17))
        self.CH_ForceHideOverlay.setText("Don\'t show overlay on-screen")
        self.CH_ForceHideOverlay.setToolTip("The overlay won't show directly on your screen. You can use this setting for example when it's meant to be visible only on stream.")

        # Replay folder
        self.LA_AccountFolder = QtWidgets.QLabel(self.TAB_Main)
        self.LA_AccountFolder.setGeometry(QtCore.QRect(520, 15, 280, 16))
        self.LA_AccountFolder.setText("Specify your StarCraft II Account folder")

        self.LA_CurrentReplayFolder = QtWidgets.QLabel(self.TAB_Main)
        self.LA_CurrentReplayFolder.setEnabled(False)
        self.LA_CurrentReplayFolder.setGeometry(QtCore.QRect(520, 25, 400, 31))

        self.BT_ChooseFolder = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_ChooseFolder.setGeometry(QtCore.QRect(520, 55, 150, 23))
        self.BT_ChooseFolder.setText('Choose folder')
        self.BT_ChooseFolder.setToolTip('Choose your account folder.\nThis is usually not necessary and the app will find its location automatically.')
        self.BT_ChooseFolder.clicked.connect(self.findReplayFolder)

        # Info label
        self.LA_InfoLabel = QtWidgets.QLabel(self.TAB_Main)
        self.LA_InfoLabel.setGeometry(QtCore.QRect(20, 400, 800, 23))

        # Apply
        self.BT_MainApply = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_MainApply.setGeometry(QtCore.QRect(867, 400, 75, 23))
        self.BT_MainApply.setText('Apply')
        self.BT_MainApply.clicked.connect(self.saveSettings)

        # Reset
        self.BT_MainReset = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_MainReset.setGeometry(QtCore.QRect(785, 400, 75, 23))
        self.BT_MainReset.setText('Reset')
        self.BT_MainReset.clicked.connect(self.resetSettings)        

        ### Hotkey frame
        self.FR_HotkeyFrame = QtWidgets.QFrame(self.TAB_Main)
        self.FR_HotkeyFrame.setGeometry(QtCore.QRect(20, 170, 411, 211))
        self.FR_HotkeyFrame.setAutoFillBackground(True)
        self.FR_HotkeyFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_HotkeyFrame.setFrameShadow(QtWidgets.QFrame.Plain)

        # Label
        self.LA_Hotkeys = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_Hotkeys.setGeometry(QtCore.QRect(0, 10, 431, 20))
        self.LA_Hotkeys.setStyleSheet("font-weight: bold")
        self.LA_Hotkeys.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Hotkeys.setText("Hotkeys")

        # Show/hide
        self.LA_ShowHide = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_ShowHide.setGeometry(QtCore.QRect(20, 50, 111, 20))
        self.LA_ShowHide.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_ShowHide.setText("Show / hide")

        self.KEY_ShowHide = CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_ShowHide.setGeometry(QtCore.QRect(20, 70, 113, 20))
        self.KEY_ShowHide.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.KEY_ShowHide.setToolTip('The key for both showing and hiding the overlay')
        
        # Show
        self.LA_Show = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_Show.setGeometry(QtCore.QRect(150, 50, 111, 20))
        self.LA_Show.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Show.setText("Show only")

        self.KEY_Show = CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Show.setGeometry(QtCore.QRect(150, 70, 113, 20))
        self.KEY_Show.setToolTip('The key for just showing the overlay')

        # Hide
        self.LA_Hide = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_Hide.setGeometry(QtCore.QRect(280, 50, 111, 20))
        self.LA_Hide.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Hide.setText("Hide only")
        
        self.KEY_Hide = CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Hide.setGeometry(QtCore.QRect(280, 70, 113, 20))
        self.KEY_Hide.setToolTip('The key for just hiding the overlay')

        # Newer
        self.LA_Newer = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_Newer.setGeometry(QtCore.QRect(20, 120, 111, 20))
        self.LA_Newer.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Newer.setText("Show newer replay")

        self.KEY_Newer = CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Newer.setGeometry(QtCore.QRect(20, 140, 113, 20))
        self.KEY_Newer.setToolTip('The key for showing a newer replay than is currently displayed')

        # Older
        self.LA_Older = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_Older.setGeometry(QtCore.QRect(150, 120, 111, 20))
        self.LA_Older.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Older.setText("Show older replay")

        self.KEY_Older = CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Older.setGeometry(QtCore.QRect(150, 140, 113, 20))
        self.KEY_Older.setToolTip('The key for showing an older replay than is currently displayed')

        # Winrates
        self.LA_Winrates = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_Winrates.setGeometry(QtCore.QRect(280, 120, 111, 20))
        self.LA_Winrates.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Winrates.setText("Show player winrates")

        self.KEY_Winrates = CustomKeySequenceEdit(self.FR_HotkeyFrame)
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

        # Note
        self.LA_More = QtWidgets.QLabel(self.FR_CustomizeColors)
        self.LA_More.setEnabled(False)
        self.LA_More.setGeometry(QtCore.QRect(0, 19, 241, 31))
        self.LA_More.setAlignment(QtCore.Qt.AlignCenter)

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

        self.ED_AomSecretKey = QtWidgets.QLineEdit(self.FR_Aom)
        self.ED_AomSecretKey.setGeometry(QtCore.QRect(62, 90, 121, 20))
        self.ED_AomSecretKey.setAlignment(QtCore.Qt.AlignCenter)
        self.ED_AomSecretKey.setPlaceholderText("secret key")
        self.ED_AomSecretKey.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)

        self.ED_AomAccount = QtWidgets.QLineEdit(self.FR_Aom)
        self.ED_AomAccount.setGeometry(QtCore.QRect(62, 60, 121, 20))
        self.ED_AomAccount.setAlignment(QtCore.Qt.AlignCenter)
        self.ED_AomAccount.setPlaceholderText("account name")

        self.BT_AomTest = QtWidgets.QPushButton(self.FR_Aom)
        self.BT_AomTest.setGeometry(QtCore.QRect(75, 150, 85, 23))
        self.BT_AomTest.clicked.connect(self.validateAOM)
        self.BT_AomTest.setText("Verify") 
        self.BT_AomTest.setToolTip("Test if the combination of the account name and the secret key is valid")    


        # Version
        self.LA_Version = QtWidgets.QLabel(self.TAB_Main)
        self.LA_Version.setGeometry(QtCore.QRect(825, 560, 141, 20))
        self.LA_Version.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing)
        self.LA_Version.setText(f"The app is up to date ({str(APPVERSION)[0]}.{str(APPVERSION)[1:]})")
        self.LA_Version.setEnabled(False)        

        # Finalize main tab
        TabWidget.addTab(self.TAB_Main, "")
        TabWidget.setTabText(TabWidget.indexOf(self.TAB_Main), "Settings")




        ### PLAYERS TAB ###
        self.TAB_Players = QtWidgets.QWidget()


        self.SC_PlayersScrollArea = QtWidgets.QScrollArea(self.TAB_Players)
        self.SC_PlayersScrollArea.setGeometry(QtCore.QRect(10, 10, 961, 561))
        self.SC_PlayersScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.SC_PlayersScrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.SC_PlayersScrollArea.setWidgetResizable(True)
        self.SC_PlayersScrollAreaContents = QtWidgets.QWidget()
        self.SC_PlayersScrollAreaContents.setGeometry(QtCore.QRect(0, 0, 961, 561))
        self.FR_Player_00 = QtWidgets.QFrame(self.SC_PlayersScrollAreaContents)
        self.FR_Player_00.setGeometry(QtCore.QRect(10, 40, 841, 41))
        self.FR_Player_00.setAutoFillBackground(False)
        self.FR_Player_00.setStyleSheet("")
        self.FR_Player_00.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_Player_00.setFrameShadow(QtWidgets.QFrame.Raised)
        self.LA_Name_00 = QtWidgets.QLabel(self.FR_Player_00)
        self.LA_Name_00.setGeometry(QtCore.QRect(20, 10, 47, 21))
        self.LA_Wins_00 = QtWidgets.QLabel(self.FR_Player_00)
        self.LA_Wins_00.setGeometry(QtCore.QRect(150, 10, 31, 21))
        self.LA_Wins_00.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Losses_00 = QtWidgets.QLabel(self.FR_Player_00)
        self.LA_Losses_00.setGeometry(QtCore.QRect(210, 10, 41, 21))
        self.LA_Losses_00.setAlignment(QtCore.Qt.AlignCenter)
        self.ED_Note_00 = QtWidgets.QLineEdit(self.FR_Player_00)
        self.ED_Note_00.setGeometry(QtCore.QRect(410, 10, 281, 21))
        self.ED_Note_00.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Winrate_00 = QtWidgets.QLabel(self.FR_Player_00)
        self.LA_Winrate_00.setGeometry(QtCore.QRect(280, 10, 51, 21))
        self.LA_Winrate_00.setAlignment(QtCore.Qt.AlignCenter)
        self.LINE_Player_00 = QtWidgets.QFrame(self.FR_Player_00)
        self.LINE_Player_00.setGeometry(QtCore.QRect(10, 0, 831, 2))
        self.LINE_Player_00.setFrameShape(QtWidgets.QFrame.HLine)
        self.LINE_Player_00.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.FR_WinratesHeading = QtWidgets.QFrame(self.SC_PlayersScrollAreaContents)
        self.FR_WinratesHeading.setGeometry(QtCore.QRect(10, 10, 841, 31))
        self.FR_WinratesHeading.setStyleSheet("font-weight:bold")
        self.FR_WinratesHeading.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_WinratesHeading.setFrameShadow(QtWidgets.QFrame.Raised)
        self.LA_Note = QtWidgets.QLabel(self.FR_WinratesHeading)
        self.LA_Note.setGeometry(QtCore.QRect(410, 0, 281, 31))
        self.LA_Note.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Losses = QtWidgets.QLabel(self.FR_WinratesHeading)
        self.LA_Losses.setGeometry(QtCore.QRect(210, 0, 41, 31))
        self.LA_Winrate = QtWidgets.QLabel(self.FR_WinratesHeading)
        self.LA_Winrate.setGeometry(QtCore.QRect(280, 0, 51, 31))
        self.LA_Winrate.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Name = QtWidgets.QLabel(self.FR_WinratesHeading)
        self.LA_Name.setGeometry(QtCore.QRect(20, 0, 41, 31))
        self.LA_Wins = QtWidgets.QLabel(self.FR_WinratesHeading)
        self.LA_Wins.setGeometry(QtCore.QRect(150, 0, 31, 31))
        self.SC_PlayersScrollArea.setWidget(self.SC_PlayersScrollAreaContents)
        TabWidget.addTab(self.TAB_Players, "")
        self.TAB_Games = QtWidgets.QWidget()
        self.SC_GamesScrollArea = QtWidgets.QScrollArea(self.TAB_Games)
        self.SC_GamesScrollArea.setGeometry(QtCore.QRect(10, 10, 961, 561))
        self.SC_GamesScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.SC_GamesScrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.SC_GamesScrollArea.setWidgetResizable(True)
        self.SC_GamesScrollAreaContent = QtWidgets.QWidget()
        self.SC_GamesScrollAreaContent.setGeometry(QtCore.QRect(0, 0, 961, 561))
        self.FR_Map_00 = QtWidgets.QFrame(self.SC_GamesScrollAreaContent)
        self.FR_Map_00.setGeometry(QtCore.QRect(10, 40, 931, 41))
        self.FR_Map_00.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_Map_00.setFrameShadow(QtWidgets.QFrame.Raised)
        self.LA_Map_Name_00 = QtWidgets.QLabel(self.FR_Map_00)
        self.LA_Map_Name_00.setGeometry(QtCore.QRect(20, 10, 91, 21))
        self.LA_Map_Name_00.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LA_Map_Result_00 = QtWidgets.QLabel(self.FR_Map_00)
        self.LA_Map_Result_00.setGeometry(QtCore.QRect(150, 10, 21, 21))
        self.LA_Map_Result_00.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Map_P1_00 = QtWidgets.QLabel(self.FR_Map_00)
        self.LA_Map_P1_00.setGeometry(QtCore.QRect(210, 10, 101, 21))
        self.LA_Map_P1_00.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Map_P2_00 = QtWidgets.QLabel(self.FR_Map_00)
        self.LA_Map_P2_00.setGeometry(QtCore.QRect(350, 10, 101, 21))
        self.LA_Map_P2_00.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Map_Enemy_00 = QtWidgets.QLabel(self.FR_Map_00)
        self.LA_Map_Enemy_00.setGeometry(QtCore.QRect(480, 10, 41, 20))
        self.LA_Map_Enemy_00.setAlignment(QtCore.Qt.AlignCenter)
        self.BT_Show_Map_00 = QtWidgets.QPushButton(self.FR_Map_00)
        self.BT_Show_Map_00.setGeometry(QtCore.QRect(850, 10, 75, 23))
        self.LA_Map_Length_00 = QtWidgets.QLabel(self.FR_Map_00)
        self.LA_Map_Length_00.setGeometry(QtCore.QRect(530, 10, 71, 20))
        self.LA_Map_Length_00.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Map_Difficulty_00 = QtWidgets.QLabel(self.FR_Map_00)
        self.LA_Map_Difficulty_00.setGeometry(QtCore.QRect(590, 10, 81, 20))
        self.LA_Map_Difficulty_00.setAlignment(QtCore.Qt.AlignCenter)
        self.BT_Find_Map_00 = QtWidgets.QPushButton(self.FR_Map_00)
        self.BT_Find_Map_00.setGeometry(QtCore.QRect(760, 10, 75, 23))
        self.LINE_Map_00 = QtWidgets.QFrame(self.FR_Map_00)
        self.LINE_Map_00.setGeometry(QtCore.QRect(10, 0, 921, 2))
        self.LINE_Map_00.setFrameShape(QtWidgets.QFrame.HLine)
        self.LINE_Map_00.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.LA_Map_Date_00 = QtWidgets.QLabel(self.FR_Map_00)
        self.LA_Map_Date_00.setGeometry(QtCore.QRect(660, 10, 81, 20))
        self.LA_Map_Date_00.setAlignment(QtCore.Qt.AlignCenter)
        self.FR_RecentGamesHeading = QtWidgets.QFrame(self.SC_GamesScrollAreaContent)
        self.FR_RecentGamesHeading.setGeometry(QtCore.QRect(10, 10, 931, 31))
        self.FR_RecentGamesHeading.setStyleSheet("font-weight: bold")
        self.FR_RecentGamesHeading.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_RecentGamesHeading.setFrameShadow(QtWidgets.QFrame.Raised)
        self.LA_Difficulty = QtWidgets.QLabel(self.FR_RecentGamesHeading)
        self.LA_Difficulty.setGeometry(QtCore.QRect(590, 0, 81, 31))
        self.LA_Difficulty.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Player2 = QtWidgets.QLabel(self.FR_RecentGamesHeading)
        self.LA_Player2.setGeometry(QtCore.QRect(360, 0, 81, 31))
        self.LA_Player2.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Enemy = QtWidgets.QLabel(self.FR_RecentGamesHeading)
        self.LA_Enemy.setGeometry(QtCore.QRect(480, 0, 41, 31))
        self.LA_Enemy.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Length = QtWidgets.QLabel(self.FR_RecentGamesHeading)
        self.LA_Length.setGeometry(QtCore.QRect(530, 0, 71, 31))
        self.LA_Length.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Map = QtWidgets.QLabel(self.FR_RecentGamesHeading)
        self.LA_Map.setGeometry(QtCore.QRect(20, 0, 41, 31))
        self.LA_Map.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LA_Player1 = QtWidgets.QLabel(self.FR_RecentGamesHeading)
        self.LA_Player1.setGeometry(QtCore.QRect(220, 0, 81, 31))
        self.LA_Player1.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Result = QtWidgets.QLabel(self.FR_RecentGamesHeading)
        self.LA_Result.setGeometry(QtCore.QRect(140, 0, 41, 31))
        self.LA_Result.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Date = QtWidgets.QLabel(self.FR_RecentGamesHeading)
        self.LA_Date.setGeometry(QtCore.QRect(660, 0, 81, 31))
        self.LA_Date.setAlignment(QtCore.Qt.AlignCenter)
        self.SC_GamesScrollArea.setWidget(self.SC_GamesScrollAreaContent)
        TabWidget.addTab(self.TAB_Games, "")
        self.TAB_Stats = QtWidgets.QWidget()
        self.FR_Stats = QtWidgets.QFrame(self.TAB_Stats)
        self.FR_Stats.setGeometry(QtCore.QRect(10, 10, 911, 151))
        self.FR_Stats.setAutoFillBackground(False)
        self.FR_Stats.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.FR_Stats.setFrameShadow(QtWidgets.QFrame.Plain)
        self.FR_Stats.setLineWidth(1)
        self.FR_Stats.setMidLineWidth(0)
        self.LA_MaxGamelength = QtWidgets.QLabel(self.FR_Stats)
        self.LA_MaxGamelength.setGeometry(QtCore.QRect(450, 40, 131, 16))
        self.SP_MinGamelength = QtWidgets.QSpinBox(self.FR_Stats)
        self.SP_MinGamelength.setGeometry(QtCore.QRect(400, 10, 42, 22))
        self.SP_MinGamelength.setMaximum(1000)
        self.SP_MinGamelength.setProperty("value", 0)
        self.SP_MaxGamelength = QtWidgets.QSpinBox(self.FR_Stats)
        self.SP_MaxGamelength.setGeometry(QtCore.QRect(400, 40, 42, 22))
        self.SP_MaxGamelength.setMinimum(0)
        self.SP_MaxGamelength.setMaximum(1000)
        self.SP_MaxGamelength.setProperty("value", 0)
        self.CH_DiffHard = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffHard.setGeometry(QtCore.QRect(10, 50, 101, 17))
        self.CH_DiffHard.setChecked(True)
        self.CH_TypeNormal = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_TypeNormal.setGeometry(QtCore.QRect(180, 10, 101, 17))
        self.CH_TypeNormal.setChecked(True)
        self.CH_TypeMutation = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_TypeMutation.setGeometry(QtCore.QRect(180, 30, 101, 17))
        self.CH_TypeMutation.setChecked(True)
        self.CH_DiffNormal = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffNormal.setGeometry(QtCore.QRect(10, 30, 61, 17))
        self.CH_DiffNormal.setChecked(True)
        self.TM_FromDate = QtWidgets.QDateEdit(self.FR_Stats)
        self.TM_FromDate.setGeometry(QtCore.QRect(620, 10, 110, 22))
        self.TM_FromDate.setDateTime(QtCore.QDateTime(QtCore.QDate(2015, 11, 10), QtCore.QTime(0, 0, 0)))
        self.TM_ToDate = QtWidgets.QDateEdit(self.FR_Stats)
        self.TM_ToDate.setGeometry(QtCore.QRect(620, 40, 110, 22))
        self.TM_ToDate.setDateTime(QtCore.QDateTime(QtCore.QDate(2030, 12, 30), QtCore.QTime(0, 0, 0)))
        self.CH_DiffCasual = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffCasual.setGeometry(QtCore.QRect(10, 10, 61, 17))
        self.CH_DiffCasual.setChecked(True)
        self.LA_MinGamelength = QtWidgets.QLabel(self.FR_Stats)
        self.LA_MinGamelength.setGeometry(QtCore.QRect(450, 10, 131, 16))
        self.BT_Generate = QtWidgets.QPushButton(self.FR_Stats)
        self.BT_Generate.setGeometry(QtCore.QRect(770, 120, 131, 31))
        self.CH_DiffBrutal = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffBrutal.setGeometry(QtCore.QRect(10, 70, 51, 17))
        self.CH_DiffBrutal.setChecked(True)
        self.LA_FromDate = QtWidgets.QLabel(self.FR_Stats)
        self.LA_FromDate.setGeometry(QtCore.QRect(740, 10, 61, 16))
        self.LA_ToDate = QtWidgets.QLabel(self.FR_Stats)
        self.LA_ToDate.setGeometry(QtCore.QRect(740, 40, 61, 16))
        self.LA_CurrentAccountNames = QtWidgets.QLabel(self.FR_Stats)
        self.LA_CurrentAccountNames.setGeometry(QtCore.QRect(10, 130, 741, 20))
        self.CH_DiffBrutalPlus = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DiffBrutalPlus.setGeometry(QtCore.QRect(10, 90, 61, 17))
        self.CH_DiffBrutalPlus.setChecked(True)
        self.CH_Region_NA = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Region_NA.setGeometry(QtCore.QRect(90, 10, 71, 17))
        self.CH_Region_NA.setChecked(True)
        self.CH_Region_EU = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Region_EU.setGeometry(QtCore.QRect(90, 30, 71, 17))
        self.CH_Region_EU.setChecked(True)
        self.CH_Region_KR = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Region_KR.setGeometry(QtCore.QRect(90, 50, 61, 17))
        self.CH_Region_KR.setChecked(True)
        self.CH_Region_CN = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Region_CN.setGeometry(QtCore.QRect(90, 70, 61, 17))
        self.CH_Region_CN.setChecked(True)
        self.CH_Region_PTR = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Region_PTR.setGeometry(QtCore.QRect(90, 90, 61, 17))
        self.CH_Region_PTR.setChecked(True)
        self.TBD1 = QtWidgets.QLabel(self.TAB_Stats)
        self.TBD1.setGeometry(QtCore.QRect(20, 230, 111, 21))
        self.TBD2 = QtWidgets.QLabel(self.TAB_Stats)
        self.TBD2.setGeometry(QtCore.QRect(20, 260, 221, 21))
        self.TBD4 = QtWidgets.QLabel(self.TAB_Stats)
        self.TBD4.setGeometry(QtCore.QRect(20, 290, 311, 21))
        self.TBD3 = QtWidgets.QLabel(self.TAB_Stats)
        self.TBD3.setGeometry(QtCore.QRect(20, 320, 421, 21))
        self.TBD5 = QtWidgets.QLabel(self.TAB_Stats)
        self.TBD5.setGeometry(QtCore.QRect(20, 350, 111, 21))
        self.TBD6 = QtWidgets.QLabel(self.TAB_Stats)
        self.TBD6.setGeometry(QtCore.QRect(20, 380, 271, 21))
        self.line = QtWidgets.QFrame(self.TAB_Stats)
        self.line.setGeometry(QtCore.QRect(10, 160, 911, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.FR_Fastest_VT = QtWidgets.QFrame(self.TAB_Stats)
        self.FR_Fastest_VT.setGeometry(QtCore.QRect(20, 380, 421, 201))
        self.FR_Fastest_VT.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_Fastest_VT.setFrameShadow(QtWidgets.QFrame.Raised)
        self.LA_Fastest_Map_VT = QtWidgets.QLabel(self.FR_Fastest_VT)
        self.LA_Fastest_Map_VT.setGeometry(QtCore.QRect(10, 10, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.LA_Fastest_Map_VT.setFont(font)
        self.BT_Fastest_Find_VT = QtWidgets.QPushButton(self.FR_Fastest_VT)
        self.BT_Fastest_Find_VT.setGeometry(QtCore.QRect(330, 10, 75, 23))
        self.LA_Fastest_P1_VT = QtWidgets.QLabel(self.FR_Fastest_VT)
        self.LA_Fastest_P1_VT.setGeometry(QtCore.QRect(10, 40, 171, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.LA_Fastest_P1_VT.setFont(font)
        self.LA_Fastest_P2_VT = QtWidgets.QLabel(self.FR_Fastest_VT)
        self.LA_Fastest_P2_VT.setGeometry(QtCore.QRect(240, 40, 201, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.LA_Fastest_P2_VT.setFont(font)
        self.LA_Fastest_P1Mastery_VT = QtWidgets.QLabel(self.FR_Fastest_VT)
        self.LA_Fastest_P1Mastery_VT.setGeometry(QtCore.QRect(10, 80, 171, 91))
        self.LA_Fastest_TimeRace_VT = QtWidgets.QLabel(self.FR_Fastest_VT)
        self.LA_Fastest_TimeRace_VT.setGeometry(QtCore.QRect(160, 10, 111, 20))
        self.LA_Fastest_P2Mastery_VT = QtWidgets.QLabel(self.FR_Fastest_VT)
        self.LA_Fastest_P2Mastery_VT.setGeometry(QtCore.QRect(240, 80, 171, 91))
        TabWidget.addTab(self.TAB_Stats, "")


        ### LINKS ###
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
        self.IMG_GitHub.setPixmap(QtGui.QPixmap(filePath("src/github.png")))

        self.LA_GitHub = QtWidgets.QLabel(self.FR_Links)
        self.LA_GitHub.setGeometry(QtCore.QRect(70, 20, 131, 41))
        self.LA_GitHub.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LA_GitHub.setText('<a href="https://github.com/FluffyMaguro/SC2_Coop_overlay">GitHub</a>')
        self.LA_GitHub.setToolTip('github.com/FluffyMaguro/SC2_Coop_overlay')

        # Maguro.one
        self.IMG_MaguroOne = QtWidgets.QLabel(self.FR_Links)
        self.IMG_MaguroOne.setGeometry(QtCore.QRect(20, 70, 31, 41))
        self.IMG_MaguroOne.setPixmap(QtGui.QPixmap(filePath("src/maguro.jpg")))

        self.LA_MaguroOne = QtWidgets.QLabel(self.FR_Links)
        self.LA_MaguroOne.setGeometry(QtCore.QRect(70, 70, 131, 41))
        self.LA_MaguroOne.setText('<a href="www.maguro.one">Maguro.one</a>')
        self.LA_MaguroOne.setToolTip('www.maguro.one')

        # Twitter
        self.IMG_Twitter = QtWidgets.QLabel(self.FR_Links)
        self.IMG_Twitter.setGeometry(QtCore.QRect(20, 120, 41, 51))
        self.IMG_Twitter.setPixmap(QtGui.QPixmap(filePath("src/twitter.png")))

        self.LA_Twitter = QtWidgets.QLabel(self.FR_Links)
        self.LA_Twitter.setGeometry(QtCore.QRect(70, 130, 131, 31))
        self.LA_Twitter.setText('<a href="https://twitter.com/FluffyMaguro">Twitter</a>')
        self.LA_Twitter.setToolTip('twitter.com/FluffyMaguro')

        # Subreddit
        self.IMG_Reddit = QtWidgets.QLabel(self.FR_Links)
        self.IMG_Reddit.setGeometry(QtCore.QRect(240, 10, 41, 51))
        self.IMG_Reddit.setPixmap(QtGui.QPixmap(filePath("src/reddit.png")))

        self.LA_Subreddit = QtWidgets.QLabel(self.FR_Links)
        self.LA_Subreddit.setGeometry(QtCore.QRect(290, 20, 161, 31))
        self.LA_Subreddit.setText('<a href="https://www.reddit.com/r/starcraft2coop/">Co-op subreddit</a>')
        self.LA_Subreddit.setToolTip('www.reddit.com/r/starcraft2coop/')

        # Forums
        self.IMG_BattleNet = QtWidgets.QLabel(self.FR_Links)
        self.IMG_BattleNet.setGeometry(QtCore.QRect(240, 60, 41, 51))
        self.IMG_BattleNet.setPixmap(QtGui.QPixmap(filePath("src/sc2.png")))

        self.LA_BattleNet = QtWidgets.QLabel(self.FR_Links)
        self.LA_BattleNet.setGeometry(QtCore.QRect(290, 70, 141, 31))
        self.LA_BattleNet.setText('<a href="https://us.forums.blizzard.com/en/sc2/c/co-op-missions-discussion">Co-op forums</a>')
        self.LA_BattleNet.setToolTip('us.forums.blizzard.com/en/sc2/c/co-op-missions-discussion')

        # Discord
        self.IMG_Discord = QtWidgets.QLabel(self.FR_Links)
        self.IMG_Discord.setGeometry(QtCore.QRect(240, 120, 31, 41))
        self.IMG_Discord.setPixmap(QtGui.QPixmap(filePath("src/discord.png")))
        
        self.LA_Discord = QtWidgets.QLabel(self.FR_Links)
        self.LA_Discord.setGeometry(QtCore.QRect(290, 120, 141, 41))
        self.LA_Discord.setText('<a href="https://discord.gg/VQnXMdm">Co-op discord</a>')
        self.LA_Discord.setToolTip('StarCraft 2 Co-op discord')

        # Donate
        self.FR_Donate = QtWidgets.QFrame(self.TAB_Links)
        self.FR_Donate.setGeometry(QtCore.QRect(20, 225, 471, 50))
        self.FR_Donate.setAutoFillBackground(True)
        self.FR_Donate.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_Donate.setFrameShadow(QtWidgets.QFrame.Plain)

        self.IMG_Donate = QtWidgets.QLabel(self.FR_Donate)
        self.IMG_Donate.setGeometry(QtCore.QRect(20, 6, 200, 41))
        self.IMG_Donate.setPixmap(QtGui.QPixmap(filePath("src/paypal.png")))

        self.LA_Donate = QtWidgets.QLabel(self.FR_Donate)
        self.LA_Donate.setGeometry(QtCore.QRect(185, 7, 250, 41))
        self.LA_Donate.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LA_Donate.setText('<a href="https://www.paypal.com/paypalme/FluffyMaguro">donate if you feel generous</a>')

        # Styling
        for item in {self.LA_MaguroOne, self.LA_Subreddit, self.LA_Twitter, self.LA_GitHub, self.LA_Discord, self.LA_BattleNet, self.LA_Donate}:
            item.setStyleSheet("font-size: 18px; color: blue; text-decoration: underline")
            item.setOpenExternalLinks(True)


        TabWidget.addTab(self.TAB_Links, "")
        TabWidget.setTabText(TabWidget.indexOf(self.TAB_Links), "Links")


        # Finalization
        self.retranslateUi(TabWidget)
        TabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(TabWidget)


    ### Methods

    def loadSettings(self):
        """ Loads settings from the config file if there is any, updates UI elements accordingly"""

        self.default_settings = {
            'start_with_windows':False,
            'start_minimized':False,
            'enable_logging':False,
            'show_player_winrates':True,
            'duration':60,
            'monitor':1,
            'force_hide_overlay':False,  
            'replay_folder':None,                  
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
            'player_notes':None
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

        # Check if account directory valid, update if not
        self.settings['replay_folder'] = get_account_dir(self.settings['replay_folder'])

        self.updateUI()


    def updateUI(self):
        """ Update UI elements based on the current settings """
        self.CH_StartWithWindows.setChecked(self.settings['start_with_windows'])
        self.CH_StartMinimized.setChecked(self.settings['start_minimized'])
        self.CH_EnableLogging.setChecked(self.settings['enable_logging'])
        self.CH_ShowPlayerWinrates.setChecked(self.settings['show_player_winrates'])
        self.CH_ForceHideOverlay.setChecked(self.settings['force_hide_overlay'])
        self.SP_Duration.setProperty("value", self.settings['duration'])
        self.SP_Monitor.setProperty("value", self.settings['monitor'])
        self.LA_CurrentReplayFolder.setText(f"Current: {self.settings['replay_folder']}")

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


    def resetSettings(self):
        """ Resets settings to default values and updates UI """
        self.settings = self.default_settings.copy()
        self.settings['replay_folder'] = get_account_dir(path=self.settings['replay_folder'])
        self.settings['aom_account'] = self.ED_AomAccount.text()
        self.settings['aom_secret_key'] = self.ED_AomSecretKey.text()        
        self.updateUI()
        self.saveSettings()
        self.sendInfoMessage('All settings have been reset!')


    def findReplayFolder(self):
        """ Finds and sets account folder """
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        if dialog.exec_():
            folder = dialog.selectedFiles()[0]
            if 'StarCraft' in folder and '/Accounts' in folder:
                self.settings['replay_folder'] = folder
                self.LA_CurrentReplayFolder.setText(f'Current: {folder}')
                self.sendInfoMessage(f'Account folder set succesfully! ({folder})',color='green')
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
            response = validate_aom_account_key(account, key)

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





    def retranslateUi(self, TabWidget):
        # !!! Remove this as I improve things
        _translate = QtCore.QCoreApplication.translate
        

        self.LA_Mastery.setText(_translate("TabWidget", "Mastery"))
        self.LA_Amon.setText(_translate("TabWidget", "Amon"))
        self.LA_P2.setText(_translate("TabWidget", "Player 2"))
        self.LA_CustomizeColors.setText(_translate("TabWidget", "Customize colors"))
        self.LA_P1.setText(_translate("TabWidget", "Player 1"))
        self.LA_More.setText(_translate("TabWidget", "(and more via editing custom.css)"))
        
        
        self.LA_Name_00.setText(_translate("TabWidget", "Maguro"))
        self.LA_Wins_00.setText(_translate("TabWidget", "3"))
        self.LA_Losses_00.setText(_translate("TabWidget", "3"))
        self.LA_Winrate_00.setText(_translate("TabWidget", "50%"))
        self.LA_Note.setText(_translate("TabWidget", "Player note (displayed together with winrates)"))
        self.LA_Losses.setText(_translate("TabWidget", "Losses"))
        self.LA_Winrate.setText(_translate("TabWidget", "Winrate"))
        self.LA_Name.setText(_translate("TabWidget", "Name"))
        self.LA_Wins.setText(_translate("TabWidget", "Wins"))
        TabWidget.setTabText(TabWidget.indexOf(self.TAB_Players), _translate("TabWidget", "Players"))
        self.LA_Map_Name_00.setText(_translate("TabWidget", "Mist Opportunities"))
        self.LA_Map_Result_00.setText(_translate("TabWidget", "Win"))
        self.LA_Map_P1_00.setText(_translate("TabWidget", "Maguro (Kerrigan)"))
        self.LA_Map_P2_00.setText(_translate("TabWidget", "Alfons (Raynor)"))
        self.LA_Map_Enemy_00.setText(_translate("TabWidget", "Zerg"))
        self.BT_Show_Map_00.setText(_translate("TabWidget", "Show overlay"))
        self.LA_Map_Length_00.setText(_translate("TabWidget", "27:58"))
        self.LA_Map_Difficulty_00.setText(_translate("TabWidget", "Brutal"))
        self.BT_Find_Map_00.setText(_translate("TabWidget", "Find file"))
        self.LA_Map_Date_00.setText(_translate("TabWidget", "27-5-2020"))
        self.LA_Difficulty.setText(_translate("TabWidget", "Difficulty"))
        self.LA_Player2.setText(_translate("TabWidget", "Player 2"))
        self.LA_Enemy.setText(_translate("TabWidget", "Enemy"))
        self.LA_Length.setText(_translate("TabWidget", "Length"))
        self.LA_Map.setText(_translate("TabWidget", "Map"))
        self.LA_Player1.setText(_translate("TabWidget", "Player 1"))
        self.LA_Result.setText(_translate("TabWidget", "Result"))
        self.LA_Date.setText(_translate("TabWidget", "Date"))
        TabWidget.setTabText(TabWidget.indexOf(self.TAB_Games), _translate("TabWidget", "Games"))
        self.LA_MaxGamelength.setText(_translate("TabWidget", "Max gamelength (minutes)"))
        self.CH_DiffHard.setText(_translate("TabWidget", "Hard"))
        self.CH_TypeNormal.setText(_translate("TabWidget", "Normal games"))
        self.CH_TypeMutation.setText(_translate("TabWidget", "Mutations"))
        self.CH_DiffNormal.setText(_translate("TabWidget", "Normal"))
        self.TM_FromDate.setDisplayFormat(_translate("TabWidget", "d/M/yyyy"))
        self.TM_ToDate.setDisplayFormat(_translate("TabWidget", "d/M/yyyy"))
        self.CH_DiffCasual.setText(_translate("TabWidget", "Casual"))
        self.LA_MinGamelength.setText(_translate("TabWidget", "Min gamelength (minutes)"))
        self.BT_Generate.setText(_translate("TabWidget", "Generate"))
        self.CH_DiffBrutal.setText(_translate("TabWidget", "Brutal"))
        self.LA_FromDate.setText(_translate("TabWidget", "From date"))
        self.LA_ToDate.setText(_translate("TabWidget", "To date"))
        self.LA_CurrentAccountNames.setText(_translate("TabWidget", "Main players identified as: Maguro, SeaMaguro, Potato"))
        self.CH_DiffBrutalPlus.setText(_translate("TabWidget", "Brutal+"))
        self.CH_Region_NA.setText(_translate("TabWidget", "Americas"))
        self.CH_Region_EU.setText(_translate("TabWidget", "Europe"))
        self.CH_Region_KR.setText(_translate("TabWidget", "Asia"))
        self.CH_Region_CN.setText(_translate("TabWidget", "China"))
        self.CH_Region_PTR.setText(_translate("TabWidget", "PTR"))
        self.TBD1.setText(_translate("TabWidget", "Difficulty stats"))
        self.TBD2.setText(_translate("TabWidget", "Map freq, winrate, avg victory time"))
        self.TBD4.setText(_translate("TabWidget", "Commander games, freq, median APM and winrates"))
        self.TBD3.setText(_translate("TabWidget", "Ally commander games (corrected), Ally mastery, prestige frequency, median apm"))
        self.TBD5.setText(_translate("TabWidget", "Fastest map clears"))
        self.LA_Fastest_Map_VT.setText(_translate("TabWidget", "Void Thrashing"))
        self.BT_Fastest_Find_VT.setText(_translate("TabWidget", "Find file"))
        self.LA_Fastest_P1_VT.setText(_translate("TabWidget", "Maguro (Tychus)\n"
"Legendary Outlaw (P0)"))
        self.LA_Fastest_P2_VT.setText(_translate("TabWidget", "KingDime (Mengsk)\n"
"Emperor of the Dominion (P0)"))
        self.LA_Fastest_P1Mastery_VT.setText(_translate("TabWidget", "30 sfdsf0 nsdfdf\n"
"15 sfdsfdsfdsf\n"
"30 sdfdsff\n"
"15 sdfdsfd\n"
"0 sdfdsfdf\n"
"30 sdfdsfd"))
        self.LA_Fastest_TimeRace_VT.setText(_translate("TabWidget", "11:24, Terran"))
        self.LA_Fastest_P2Mastery_VT.setText(_translate("TabWidget", "30 sfdsf0 nsdfdf\n"
"15 sfdsfdsfdsf\n"
"30 sdfdsff\n"
"15 sdfdsfd\n"
"0 sdfdsfdf\n"
"30 sdfdsfd"))
        TabWidget.setTabText(TabWidget.indexOf(self.TAB_Stats), _translate("TabWidget", "Stats"))
        



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    TabWidget = QtWidgets.QTabWidget()
    ui = UI_TabWidget()
    ui.setupUi(TabWidget)
    ui.loadSettings()
    TabWidget.show()

    # Save settings before the app is closed
    exit_event = app.exec_()
    ui.saveSettings()
    sys.exit(exit_event)
