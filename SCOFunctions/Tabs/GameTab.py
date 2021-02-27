import traceback
from PyQt5 import QtWidgets, QtGui, QtCore
import SCOFunctions.MUserInterface as MUI
from SCOFunctions.MLogging import logclass

logger = logclass('GT', 'INFO')


class GameTab(QtWidgets.QWidget):
    def __init__(self, parent, TabWidget):
        super().__init__()
        self.p = parent
        self.game_UI_dict = dict()

        # Scroll
        self.SC_GamesScrollArea = QtWidgets.QScrollArea(self)
        self.SC_GamesScrollArea.setGeometry(QtCore.QRect(0, 30, TabWidget.frameGeometry().width() - 5, TabWidget.frameGeometry().height() - 30))
        self.SC_GamesScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.SC_GamesScrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.SC_GamesScrollArea.setWidgetResizable(True)

        self.SC_GamesScrollAreaContent = QtWidgets.QWidget()
        self.SC_GamesScrollAreaContent.setGeometry(QtCore.QRect(0, 0, 931, 561))
        self.SC_GamesScrollAreaContentLayout = QtWidgets.QVBoxLayout()
        self.SC_GamesScrollAreaContentLayout.setAlignment(QtCore.Qt.AlignTop)
        self.SC_GamesScrollAreaContentLayout.setContentsMargins(10, 0, 0, 0)

        self.LA_Games_Wait = QtWidgets.QLabel(self.SC_GamesScrollAreaContent)
        self.LA_Games_Wait.setGeometry(QtCore.QRect(0, 0, self.SC_GamesScrollAreaContent.width(), self.SC_GamesScrollAreaContent.height()))
        self.LA_Games_Wait.setText('<b>Please wait. This can take few minutes the first time.<br>Analyzing your replays.</b>')
        self.LA_Games_Wait.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)

        # Heading
        self.WD_RecentGamesHeading = QtWidgets.QWidget(self)
        self.WD_RecentGamesHeading.setGeometry(QtCore.QRect(0, 0, 990, 32))
        self.WD_RecentGamesHeading.setStyleSheet("font-weight: bold")
        self.WD_RecentGamesHeading.setAutoFillBackground(True)
        self.WD_RecentGamesHeading.setBackgroundRole(QtGui.QPalette.Background)

        self.LA_Difficulty = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Difficulty.setGeometry(QtCore.QRect(580, 0, 81, 31))
        self.LA_Difficulty.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Difficulty.setText("Difficulty")

        self.LA_Player2 = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Player2.setGeometry(QtCore.QRect(305, 0, 200, 31))
        self.LA_Player2.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Player2.setText("Player 2")

        self.LA_Enemy = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Enemy.setGeometry(QtCore.QRect(485, 0, 41, 31))
        self.LA_Enemy.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Enemy.setText("Enemy")

        self.LA_Length = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Length.setGeometry(QtCore.QRect(525, 0, 71, 31))
        self.LA_Length.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Length.setText("Length")

        self.LA_Map = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Map.setGeometry(QtCore.QRect(30, 0, 125, 31))
        self.LA_Map.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.LA_Map.setText("Map")

        self.LA_Player1 = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Player1.setGeometry(QtCore.QRect(170, 0, 200, 31))
        self.LA_Player1.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Player1.setText("Player 1")

        self.LA_Result = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Result.setGeometry(QtCore.QRect(145, 0, 50, 31))
        self.LA_Result.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Result.setText("Result")

        self.LA_Date = QtWidgets.QLabel(self.WD_RecentGamesHeading)
        self.LA_Date.setGeometry(QtCore.QRect(655, 0, 101, 31))
        self.LA_Date.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Date.setText("Time")

        self.GameTabLine = MUI.Cline(self.WD_RecentGamesHeading)
        self.GameTabLine.setGeometry(QtCore.QRect(20, 30, 921, 1))

        self.ed_games_search = QtWidgets.QLineEdit(self.WD_RecentGamesHeading)
        self.ed_games_search.setGeometry(QtCore.QRect(740, 5, 160, 20))
        self.ed_games_search.setAlignment(QtCore.Qt.AlignCenter)
        self.ed_games_search.setStyleSheet("font-weight: normal")
        self.ed_games_search.setPlaceholderText("Search")
        self.ed_games_search.setToolTip("Search for any data in a game. Separate words by spaces.")

        self.bt_games_search = QtWidgets.QPushButton(self.WD_RecentGamesHeading)
        self.bt_games_search.setGeometry(QtCore.QRect(910, 3, 25, 25))
        self.bt_games_search.setStyleSheet("font-weight: normal")
        self.bt_games_search.setText("GO")
        self.bt_games_search.clicked.connect(self.search_games)
        self.bt_games_search.setShortcut("Return")

        # Finishing
        self.SC_GamesScrollAreaContent.setLayout(self.SC_GamesScrollAreaContentLayout)
        self.SC_GamesScrollArea.setWidget(self.SC_GamesScrollAreaContent)

    def initialize_data(self, CAnalysis):
        for game in CAnalysis.get_last_replays(self.p.settings['list_games']):
            self.game_UI_dict[game.file] = MUI.GameEntry(game, CAnalysis.main_handles, self.SC_GamesScrollAreaContent)
            self.SC_GamesScrollAreaContentLayout.addWidget(self.game_UI_dict[game.file].widget)

    def search_games(self):
        """ Searches for games with given strings in them and updates games tab"""

        if not hasattr(self.p, 'CAnalysis'):
            return

        search_for = [i.replace('_', ' ') for i in self.ed_games_search.text().split()]
        if len(search_for) == 0:
            # Restore default
            new_replays = self.p.CAnalysis.get_last_replays(self.p.settings['list_games'])
        else:
            # Search for replays with strings in them
            new_replays = self.p.CAnalysis.search(*search_for)
            logger.info(f'Searching games with {search_for} | found {len(new_replays)} replays')

        # Hide current replays that are not in there
        for i in range(self.SC_GamesScrollAreaContentLayout.count()):
            widget = self.SC_GamesScrollAreaContentLayout.itemAt(i).widget()
            widget.hide()

        # Add replays
        for r in new_replays[:self.p.settings['list_games']]:
            if r.file in self.game_UI_dict:
                self.SC_GamesScrollAreaContentLayout.addWidget(self.game_UI_dict[r.file].widget)
                self.game_UI_dict[r.file].widget.show()
            else:
                self.game_UI_dict[r.file] = MUI.GameEntry(r, self.p.CAnalysis.main_handles, self.SC_GamesScrollAreaContent)
                self.SC_GamesScrollAreaContentLayout.addWidget(self.game_UI_dict[r.file].widget)

    def add_new_game_data(self, replay_dict):
        """ Updates game tab, player tab, sets winrate data in MF, updates mass replay analysis and generates stats anew """

        self.p.TAB_Randomizer.RNG_Overlay_changed()

        if hasattr(self.p, 'CAnalysis') and replay_dict is not None:
            # Add game to game tab
            try:
                # Update mass replay analysis
                full_data = self.p.CAnalysis.add_parsed_replay(replay_dict)
                if full_data is None:
                    return

                # Update UI in game tab
                self.game_UI_dict[replay_dict['parser']['file']] = MUI.GameEntry(full_data, self.p.CAnalysis.main_handles,
                                                                                 self.SC_GamesScrollAreaContent)
                self.SC_GamesScrollAreaContentLayout.insertWidget(0, self.game_UI_dict[replay_dict['parser']['file']].widget)

                # Update player tab & set winrate data in MF & generate stats
                self.p.update_winrate_data()
                self.p.TAB_Stats.generate_stats()

                # Put the last player on top of player tab
                for player in {1, 2}:
                    name = replay_dict['parser']['players'][player].get('name', '-')
                    if not replay_dict['parser']['players'][player].get('handle', '-') in self.p.CAnalysis.main_handles:
                        self.p.TAB_Players.put_player_first(name)
                        break
            except:
                logger.error(traceback.format_exc())