from PyQt5 import QtWidgets, QtGui, QtCore
import SCOFunctions.MUserInterface as MUI


class PlayerTab(QtWidgets.QWidget):
    def __init__(self, parent, TabWidget):
        super().__init__()
        self.p = parent
        self.filter_players_running = False
        self.player_winrate_UI_dict = dict()
        self.last_ally_player = None

        # Controls
        self.FR_Winrate_Controls = QtWidgets.QFrame(self)
        self.FR_Winrate_Controls.setGeometry(QtCore.QRect(0, 550, TabWidget.frameGeometry().width(), 50))
        self.FR_Winrate_Controls.setAutoFillBackground(True)
        self.FR_Winrate_Controls.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_Winrate_Controls.setFrameShadow(QtWidgets.QFrame.Raised)

        # Search
        self.ED_Winrate_Search = QtWidgets.QLineEdit(self.FR_Winrate_Controls)
        self.ED_Winrate_Search.setGeometry(QtCore.QRect(65, 7, 610, 20))
        self.ED_Winrate_Search.setAlignment(QtCore.Qt.AlignCenter)
        self.ED_Winrate_Search.setPlaceholderText("Search for player name or note")
        self.ED_Winrate_Search.textChanged.connect(self.filter_players)

        # Top 50
        self.CH_OnlyTop50 = QtWidgets.QCheckBox(self.FR_Winrate_Controls)
        self.CH_OnlyTop50.setGeometry(QtCore.QRect(700, 8, 200, 17))
        self.CH_OnlyTop50.setText("Show max 50 players")
        self.CH_OnlyTop50.setToolTip("Unchecking this will likely cause lag. All players are always searched no matter the status of this setting.")
        self.CH_OnlyTop50.setChecked(True)
        self.CH_OnlyTop50.stateChanged.connect(self.filter_players)

        # Scroll
        self.SC_PlayersScrollArea = QtWidgets.QScrollArea(self)
        self.SC_PlayersScrollArea.setGeometry(QtCore.QRect(0, 31, TabWidget.frameGeometry().width() - 5, TabWidget.frameGeometry().height() - 91))
        self.SC_PlayersScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.SC_PlayersScrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.SC_PlayersScrollArea.setWidgetResizable(True)

        self.SC_PlayersScrollAreaContents = QtWidgets.QWidget()
        self.SC_PlayersScrollAreaContents.setGeometry(QtCore.QRect(0, 31, 961, 530))
        self.SC_PlayersScrollAreaContentsLayout = QtWidgets.QVBoxLayout()
        self.SC_PlayersScrollAreaContentsLayout.setAlignment(QtCore.Qt.AlignTop)
        self.SC_PlayersScrollAreaContentsLayout.setContentsMargins(10, 0, 0, 0)
        self.SC_PlayersScrollAreaContentsLayout.setSpacing(0)

        # Heading
        self.WD_WinratesHeading = QtWidgets.QWidget(self)
        self.WD_WinratesHeading.setGeometry(QtCore.QRect(0, 0, 981, 31))
        self.WD_WinratesHeading.setStyleSheet("font-weight:bold")
        self.WD_WinratesHeading.setAutoFillBackground(True)
        self.WD_WinratesHeading.setBackgroundRole(QtGui.QPalette.Background)

        self.LA_Name = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_Name.setGeometry(QtCore.QRect(30, 0, 41, 31))
        self.LA_Name.setText("Name")

        self.LA_Wins = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_Wins.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Wins.setGeometry(QtCore.QRect(145, 0, 50, 31))
        self.LA_Wins.setText("▼ Wins")

        self.LA_Losses = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_Losses.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Losses.setGeometry(QtCore.QRect(215, 0, 45, 31))
        self.LA_Losses.setText("Losses")

        self.LA_Winrate = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_Winrate.setGeometry(QtCore.QRect(270, 0, 51, 31))
        self.LA_Winrate.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Winrate.setText("Winrate")

        self.LA_PL_APM = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_PL_APM.setGeometry(QtCore.QRect(325, 0, 51, 31))
        self.LA_PL_APM.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_PL_APM.setText("APM")
        self.LA_PL_APM.setToolTip("Median APM")

        self.LA_PL_Kills = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_PL_Kills.setGeometry(QtCore.QRect(380, 0, 51, 31))
        self.LA_PL_Kills.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_PL_Kills.setText("Kills")
        self.LA_PL_Kills.setToolTip("Median percent of kills")

        self.LA_PL_Commander = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_PL_Commander.setGeometry(QtCore.QRect(430, 0, 81, 31))
        self.LA_PL_Commander.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_PL_Commander.setText("#1 Com")
        self.LA_PL_Commander.setToolTip("The most played commander")

        self.LA_PL_Frequency = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_PL_Frequency.setGeometry(QtCore.QRect(495, 0, 81, 31))
        self.LA_PL_Frequency.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_PL_Frequency.setText("Frequency")
        self.LA_PL_Frequency.setToolTip("The most played commander frequency")

        self.LA_Note = QtWidgets.QLabel(self.WD_WinratesHeading)
        self.LA_Note.setGeometry(QtCore.QRect(580, 0, 300, 31))
        self.LA_Note.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Note.setText("Player note (displayed together with winrates)")

        self.PlayerTabLine = MUI.Cline(self.WD_WinratesHeading)
        self.PlayerTabLine.setGeometry(QtCore.QRect(20, 30, 921, 1))

        # Wait
        self.LA_Winrates_Wait = QtWidgets.QLabel(self)
        self.LA_Winrates_Wait.setGeometry(QtCore.QRect(0, 0, self.SC_PlayersScrollAreaContents.width(), self.SC_PlayersScrollAreaContents.height()))
        self.LA_Winrates_Wait.setText('<b>Please wait. This can take few minutes the first time.<br>Analyzing your replays.</b>')
        self.LA_Winrates_Wait.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)

    def put_player_first(self, player):
        """ Moves a player to the top spot in the player tab.
            Returns the last player on top (if any) to its position. """

        # Return the old player
        if self.last_ally_player is not None:
            w = self.player_winrate_UI_dict[self.last_ally_player]
            self.SC_PlayersScrollAreaContentsLayout.removeWidget(w.widget)

            # Find the position where to put it back
            wins = w.wins
            for idx, pplayer in enumerate(self.player_winrate_UI_dict):
                if wins >= self.player_winrate_UI_dict[pplayer].wins and idx > 0:
                    self.SC_PlayersScrollAreaContentsLayout.insertWidget(idx + 1, w.widget)
                    break

            # Color back
            w.highlight(False)

        # New player to top
        self.last_ally_player = player
        if player in self.player_winrate_UI_dict:
            # If it's there remove
            w = self.player_winrate_UI_dict[player]
            self.SC_PlayersScrollAreaContentsLayout.removeWidget(w.widget)

        else:
            # It's not there, create new one
            self.player_winrate_UI_dict[player] = MUI.PlayerEntry(player,
                                                                    self.p.winrate_data[player],
                                                                    self.p.settings['player_notes'].get(player, None),
                                                                    self.SC_PlayersScrollAreaContents) #yapf: disable
            w = self.player_winrate_UI_dict[player]

        # Insert to top, show and change colors
        self.SC_PlayersScrollAreaContentsLayout.insertWidget(0, w.widget)
        w.highlight(True)
        w.widget.show()

    def update(self, winrate_data, show_max=50):
        """ Updates player tab based on provide winrate data """
        if self.LA_Winrates_Wait is not None:
            self.LA_Winrates_Wait.deleteLater()
            self.LA_Winrates_Wait = None

        # Create new or update top `show_nax` players
        for idx, player in enumerate(winrate_data):
            if idx >= show_max:
                break
            if not player in self.player_winrate_UI_dict:
                self.player_winrate_UI_dict[player] = MUI.PlayerEntry(player,
                                                                      winrate_data[player],
                                                                      self.p.settings['player_notes'].get(player, None),
                                                                      self.SC_PlayersScrollAreaContents) #yapf: disable
                self.SC_PlayersScrollAreaContentsLayout.addWidget(self.player_winrate_UI_dict[player].widget)
            else:
                self.player_winrate_UI_dict[player].update_winrates(winrate_data[player])

        # Show top `show_max` and hide the rest
        for idx, player in enumerate(self.player_winrate_UI_dict):
            if idx < show_max:
                self.player_winrate_UI_dict[player].show()
            else:
                self.player_winrate_UI_dict[player].hide()

        # Hide players not in winrate data
        for player in self.player_winrate_UI_dict:
            if not player in winrate_data:
                self.player_winrate_UI_dict[player].hide()

        self.SC_PlayersScrollAreaContents.setLayout(self.SC_PlayersScrollAreaContentsLayout)
        self.SC_PlayersScrollArea.setWidget(self.SC_PlayersScrollAreaContents)

    def filter_players(self):
        """ Filters only players with string in name or note """
        self.filter_players_running = True
        text = self.ED_Winrate_Search.text().lower()
        idx = 0
        show_max = 50 if self.CH_OnlyTop50.isChecked() else 10000
        created = 0

        # First hide all
        for player in self.player_winrate_UI_dict:
            self.player_winrate_UI_dict[player].hide()

        # Go through winrate data and check for player names
        for player in self.p.winrate_data:
            if text in player.lower() and idx < show_max:

                # If many created, pause for bit. Otherwise some PCs might struggle
                if created > 100:
                    self.p.wait_ms(5)
                    created = 0

                # Create element if necessary and show
                if not player in self.player_winrate_UI_dict:
                    created += 1
                    self.player_winrate_UI_dict[player] = MUI.PlayerEntry(player,
                                                                        self.p.winrate_data[player],
                                                                        self.p.settings['player_notes'].get(player, None),
                                                                        self.SC_PlayersScrollAreaContents) #yapf: disable
                    self.SC_PlayersScrollAreaContentsLayout.addWidget(self.player_winrate_UI_dict[player].widget)
                self.player_winrate_UI_dict[player].show()
                idx += 1

        # Go though notes
        for player, note in self.p.settings['player_notes'].items():
            if text in note.lower() and idx < show_max:
                # Create element if necessary and show
                if not player in self.player_winrate_UI_dict:
                    self.player_winrate_UI_dict[player] = MUI.PlayerEntry(player,
                                                                        self.p.winrate_data[player],
                                                                        self.p.settings['player_notes'].get(player, None),
                                                                        self.SC_PlayersScrollAreaContents) #yapf: disable
                    self.SC_PlayersScrollAreaContentsLayout.addWidget(self.player_winrate_UI_dict[player].widget)
                self.player_winrate_UI_dict[player].show()
                idx += 1

        # Finished
        self.filter_players_running = False