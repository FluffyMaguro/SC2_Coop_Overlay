from functools import partial
from PyQt5 import QtWidgets, QtGui, QtCore
import SCOFunctions.MUserInterface as MUI
from SCOFunctions.MLogging import logclass

logger = logclass('STATS', 'INFO')


class StatsTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.p = parent
        self.stats_maps_UI_dict = dict()
        self.stats_region_UI_dict = dict()
        self.stats_mycommander_UI_dict = dict()
        self.stats_allycommander_UI_dict = dict()

        self.FR_Stats = QtWidgets.QFrame(self)
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

        self.CH_AllHistoric = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_AllHistoric.setGeometry(QtCore.QRect(290, 20, 180, 17))
        self.CH_AllHistoric.setChecked(True)
        self.CH_AllHistoric.setText("Override folder selection")
        self.CH_AllHistoric.setToolTip("Shows stats from all replays regardless of which folder is selected")
        self.CH_AllHistoric.stateChanged.connect(self.generate_stats)

        self.CH_DualMain = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_DualMain.setGeometry(QtCore.QRect(290, 40, 250, 17))
        self.CH_DualMain.setChecked(False)
        self.CH_DualMain.setText("Include multi-box games")
        self.CH_DualMain.setToolTip("Include games where both players belong to your accounts")
        self.CH_DualMain.stateChanged.connect(self.generate_stats)

        # Sub15 and both mains
        self.CH_Sub15 = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Sub15.setGeometry(QtCore.QRect(290, 60, 150, 17))
        self.CH_Sub15.setChecked(True)
        self.CH_Sub15.setText("Include levels 1-14")
        self.CH_Sub15.setToolTip("Include games where the main player was level 1-14")
        self.CH_Sub15.stateChanged.connect(self.generate_stats)

        self.CH_Over15 = QtWidgets.QCheckBox(self.FR_Stats)
        self.CH_Over15.setGeometry(QtCore.QRect(290, 80, 150, 17))
        self.CH_Over15.setChecked(True)
        self.CH_Over15.setText("Include levels 15+")
        self.CH_Over15.setToolTip("Include games where the main player was level 15+")
        self.CH_Over15.stateChanged.connect(self.generate_stats)

        # Games found
        self.LA_GamesFound = QtWidgets.QLabel(self.FR_Stats)
        self.LA_GamesFound.setEnabled(False)
        self.LA_GamesFound.setGeometry(QtCore.QRect(570, 110, 381, 20))
        self.LA_GamesFound.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.LA_GamesFound.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        # Main names
        self.LA_IdentifiedPlayers = QtWidgets.QLabel(self.FR_Stats)
        self.LA_IdentifiedPlayers.setEnabled(False)
        self.LA_IdentifiedPlayers.setGeometry(QtCore.QRect(570, 125, 381, 20))
        self.LA_IdentifiedPlayers.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.LA_IdentifiedPlayers.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        # Date time frame
        self.FR_DateTime = QtWidgets.QFrame(self.FR_Stats)
        self.FR_DateTime.setGeometry(QtCore.QRect(470, 15, 500, 300))

        # Date
        self.LA_ReplayDate = QtWidgets.QLabel(self.FR_DateTime)
        self.LA_ReplayDate.setGeometry(QtCore.QRect(160, 0, 101, 16))
        self.LA_ReplayDate.setStyleSheet('font-weight: bold')
        self.LA_ReplayDate.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
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
        self.LA_GameLength.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
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

        # Data dump
        self.BT_FA_dump = QtWidgets.QPushButton(self.FR_Stats)
        self.BT_FA_dump.setGeometry(QtCore.QRect(850, 10, 100, 25))
        self.BT_FA_dump.setText('Dump Data')
        self.BT_FA_dump.setToolTip('Dumps all replay data to "replay_data_dump.json" file')
        self.BT_FA_dump.setEnabled(False)

        ##### RESULTS #####
        self.TABW_StatResults = QtWidgets.QTabWidget(self)
        self.TABW_StatResults.setGeometry(QtCore.QRect(5, 126, 971, 459))

        ### TAB Maps
        self.TAB_Maps = QtWidgets.QWidget()
        self.GB_MapsOverview = QtWidgets.QFrame(self.TAB_Maps)
        self.GB_MapsOverview.setGeometry(QtCore.QRect(8, 8, 470, 420))
        self.WD_Heading = MUI.MapEntry(self.GB_MapsOverview,
                                       0,
                                       'Map name',
                                       'Fastest',
                                       'Average',
                                       'Wins',
                                       'Losses',
                                       'Freq',
                                       'Bonus',
                                       bold=True,
                                       button=False)

        self.MapsComboBoxLabel = QtWidgets.QLabel(self.TAB_Maps)
        self.MapsComboBoxLabel.setGeometry(QtCore.QRect(485, 2, 100, 21))
        self.MapsComboBoxLabel.setText('<b>Sort by</b>')

        self.MapsComboBox = QtWidgets.QComboBox(self.TAB_Maps)
        self.MapsComboBox.setGeometry(QtCore.QRect(485, 22, 100, 21))
        self.MapsComboBox.addItem('Average time')
        self.MapsComboBox.addItem('Fastest time')
        self.MapsComboBox.addItem('Frequency')
        self.MapsComboBox.addItem('Wins')
        self.MapsComboBox.addItem('Losses')
        self.MapsComboBox.addItem('Winrate')
        self.MapsComboBox.addItem('Bonus')
        self.MapsComboBox.activated[str].connect(self.generate_stats)

        self.QB_FastestMap = MUI.FastestMap(self.TAB_Maps)

        self.LA_Stats_Wait = QtWidgets.QLabel(self.TAB_Maps)
        self.LA_Stats_Wait.setGeometry(QtCore.QRect(0, 0, 470, self.TAB_Maps.height()))
        self.LA_Stats_Wait.setText('<b>Please wait. This can take few minutes the first time.<br>Analyzing your replays.</b>')
        self.LA_Stats_Wait.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)

        ### TAB Difficulty & Regions
        self.TAB_DifficultyRegions = QtWidgets.QWidget()
        self.LA_Difficulty_header = MUI.DifficultyEntry('Difficuly',
                                                        'Wins',
                                                        'Losses',
                                                        'Winrate',
                                                        50,
                                                        0,
                                                        bold=True,
                                                        line=True,
                                                        parent=self.TAB_DifficultyRegions)
        self.ProgressionStatsHeading = MUI.RegionStats('Region', {
            'Defeat': 'Losses',
            'Victory': 'Wins',
            'frequency': 'Frequency',
            'max_asc': 'Ascension level',
            'max_com': 'Maxed commanders',
            'winrate': 'Winrate',
            'prestiges': 'Prestiges tried'
        },
                                                       0,
                                                       parent=self.TAB_DifficultyRegions,
                                                       bold=True,
                                                       line=True)

        ### TAB Commanders
        self.TAB_MyCommanders = QtWidgets.QWidget()
        self.MyCommanderHeading = MUI.CommanderEntry('Commander',
                                                     'Freq',
                                                     'Wins',
                                                     'Losses',
                                                     'Winrate',
                                                     'APM',
                                                     'Kills',
                                                     2,
                                                     bold=True,
                                                     button=False,
                                                     parent=self.TAB_MyCommanders)

        self.MyCommanderComboBoxLabel = QtWidgets.QLabel(self.TAB_MyCommanders)
        self.MyCommanderComboBoxLabel.setGeometry(QtCore.QRect(485, 2, 100, 21))
        self.MyCommanderComboBoxLabel.setText('<b>Sort by</b>')

        self.MyCommanderComboBox = QtWidgets.QComboBox(self.TAB_MyCommanders)
        self.MyCommanderComboBox.setGeometry(QtCore.QRect(485, 22, 100, 21))
        self.MyCommanderComboBox.addItem('Frequency')
        self.MyCommanderComboBox.addItem('Wins')
        self.MyCommanderComboBox.addItem('Losses')
        self.MyCommanderComboBox.addItem('Winrate')
        self.MyCommanderComboBox.addItem('APM')
        self.MyCommanderComboBox.addItem('Kills')
        self.MyCommanderComboBox.activated[str].connect(self.my_commander_sort_update)

        ### TAB Allied Commanders
        self.TAB_AlliedCommanders = QtWidgets.QWidget()
        self.LA_AlliedCommanders = QtWidgets.QLabel(self.TAB_AlliedCommanders)
        self.LA_AlliedCommanders.setGeometry(QtCore.QRect(555, 408, 400, 20))
        self.LA_AlliedCommanders.setText("* Frequency has been corrected for your commander preferences")
        self.LA_AlliedCommanders.setAlignment(QtCore.Qt.AlignRight)
        self.LA_AlliedCommanders.setEnabled(False)

        self.AlliedCommanderHeading = MUI.CommanderEntry(
            'Allied commander',
            'Freq',
            'Wins',
            'Losses',
            'Winrate',
            'APM',
            'Kills',
            2,
            bold=True,
            button=False,
            parent=self.TAB_AlliedCommanders,
        )

        self.AllyCommanderComboBoxLabel = QtWidgets.QLabel(self.TAB_AlliedCommanders)
        self.AllyCommanderComboBoxLabel.setGeometry(QtCore.QRect(485, 2, 100, 21))
        self.AllyCommanderComboBoxLabel.setText('<b>Sort by</b>')

        self.AllyCommanderComboBox = QtWidgets.QComboBox(self.TAB_AlliedCommanders)
        self.AllyCommanderComboBox.setGeometry(QtCore.QRect(485, 22, 100, 21))
        self.AllyCommanderComboBox.addItem('Frequency')
        self.AllyCommanderComboBox.addItem('Wins')
        self.AllyCommanderComboBox.addItem('Losses')
        self.AllyCommanderComboBox.addItem('Winrate')
        self.AllyCommanderComboBox.addItem('APM')
        self.AllyCommanderComboBox.addItem('Kills')
        self.AllyCommanderComboBox.activated[str].connect(self.ally_commander_sort_update)

        # Full analysis
        self.TAB_FullAnalysis = QtWidgets.QWidget()

        self.CH_FA_description = QtWidgets.QLabel(self.TAB_FullAnalysis)
        self.CH_FA_description.setGeometry(QtCore.QRect(10, 0, 500, 80))
        self.CH_FA_description.setText('Run full analysis to get more accurate game lengths and APM, and see additional statistics \
                                        related to player and unit kills, bonus objectives and other.<br><br><b>Warning! This might \
                                        take few hours and the application will be less responsive.</b>')
        self.CH_FA_description.setWordWrap(True)

        self.BT_FA_run = QtWidgets.QPushButton(self.TAB_FullAnalysis)
        self.BT_FA_run.setGeometry(QtCore.QRect(10, 85, 80, 25))
        self.BT_FA_run.setText('Run')
        self.BT_FA_run.setEnabled(False)

        self.BT_FA_stop = QtWidgets.QPushButton(self.TAB_FullAnalysis)
        self.BT_FA_stop.setGeometry(QtCore.QRect(105, 85, 80, 25))
        self.BT_FA_stop.clicked.connect(self.p.stop_full_analysis)
        self.BT_FA_stop.setText('Stop')
        self.BT_FA_stop.setEnabled(False)

        self.CH_FA_atstart = QtWidgets.QCheckBox(self.TAB_FullAnalysis)
        self.CH_FA_atstart.setGeometry(QtCore.QRect(11, 115, 300, 25))
        self.CH_FA_atstart.setText('Continue full analysis at start')

        self.CH_FA_status = QtWidgets.QLabel(self.TAB_FullAnalysis)
        self.CH_FA_status.setGeometry(QtCore.QRect(10, 140, 400, 40))

        # Putting it together
        self.TABW_StatResults.addTab(self.TAB_Maps, "")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_Maps), "Maps")

        self.TABW_StatResults.addTab(self.TAB_AlliedCommanders, "")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_AlliedCommanders), "Allied commanders")

        self.TABW_StatResults.addTab(self.TAB_MyCommanders, "")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_MyCommanders), "My commanders")

        self.TABW_StatResults.addTab(self.TAB_DifficultyRegions, "")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_DifficultyRegions), "Difficulty and regions")

        self.TABW_StatResults.addTab(self.TAB_FullAnalysis, "")
        self.TABW_StatResults.setTabText(self.TABW_StatResults.indexOf(self.TAB_FullAnalysis), "Full analysis")

        self.TABW_StatResults.setCurrentIndex(0)
        self.TABW_StatResults.currentChanged.connect(self.switched_tab)

    def generate_stats(self):
        """ Generate stats and passes data to be shown"""

        if not hasattr(self.p, 'CAnalysis'):
            logger.error('Mass analysis hasn\'t finished yet')
            return

        # Check
        if self.CH_AllHistoric.isChecked():
            self.p.CAnalysis.update_data(showAll=True)
        else:
            self.p.CAnalysis.update_data(showAll=False)

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
            difficulty_filter = difficulty_filter.union({1, 2, 3, 4, 5, 6})

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
        analysis = self.p.CAnalysis.analyse_replays(include_mutations=include_mutations,
                                                    include_normal_games=include_normal_games,
                                                    difficulty_filter=difficulty_filter,
                                                    region_filter=region_filter,
                                                    mindate=mindate,
                                                    maxdate=maxdate,
                                                    minlength=minlength,
                                                    maxLength=maxLength,
                                                    sub_15=sub_15,
                                                    over_15=over_15,
                                                    include_both_main=include_both_main)

        self.LA_GamesFound.setText(f"Games found: {analysis['games']}")

        ### Map stats

        # Delete buttons if not required
        for item in set(self.stats_maps_UI_dict.keys()):
            self.stats_maps_UI_dict[item].deleteLater()
            del self.stats_maps_UI_dict[item]

        # Sort maps
        sort_by = self.MapsComboBox.currentText()
        trans_dict = {
            'Frequency': 'frequency',
            'Wins': 'Victory',
            'Losses': 'Defeat',
            'Winrate': 'winrate',
            'Average time': 'average_victory_time',
            'Bonus': 'bonus'
        }
        trans_dict_reverse = {'Frequency': True, 'Wins': True, 'Losses': True, 'Winrate': True, 'Average time': False, 'Bonus': True}

        if sort_by == 'Fastest time':
            analysis['MapData'] = {k: v for k, v in sorted(analysis['MapData'].items(), key=lambda x: x[1]['Fastest']['length'])}
        else:
            analysis['MapData'] = {
                k: v
                for k, v in sorted(analysis['MapData'].items(), key=lambda x: x[1][trans_dict[sort_by]], reverse=trans_dict_reverse[sort_by])
            }

        # Add map buttons & update the fastest map
        idx = 0
        for m in analysis['MapData']:
            idx += 1
            self.stats_maps_UI_dict[m] = MUI.MapEntry(self.GB_MapsOverview,
                                                      idx * 25,
                                                      m,
                                                      analysis['MapData'][m]['Fastest']['length'],
                                                      analysis['MapData'][m]['average_victory_time'],
                                                      analysis['MapData'][m]['Victory'],
                                                      analysis['MapData'][m]['Defeat'],
                                                      analysis['MapData'][m]['frequency'],
                                                      analysis['MapData'][m]['bonus'],
                                                      bg=idx % 2 == 0)

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

        difficulties = ['Casual', 'Normal', 'Hard', 'Brutal', 'B+1', 'B+2', 'B+3', 'B+4', 'B+5', 'B+6']
        idx = 0
        AllDiff = {'Victory': 0, 'Defeat': 0}
        for difficulty in difficulties:
            if difficulty in analysis['DifficultyData']:
                line = True if idx + 1 == len(analysis['DifficultyData']) else False
                self.stats_difficulty_UI_dict[difficulty] = MUI.DifficultyEntry(difficulty.replace('B+', 'Brutal+'),
                                                                                analysis['DifficultyData'][difficulty]['Victory'],
                                                                                analysis['DifficultyData'][difficulty]['Defeat'],
                                                                                f"{100*analysis['DifficultyData'][difficulty]['Winrate']:.0f}%",
                                                                                50,
                                                                                idx * 18 + 20,
                                                                                bg=idx % 2,
                                                                                parent=self.TAB_DifficultyRegions,
                                                                                line=line)
                idx += 1
                AllDiff['Victory'] += analysis['DifficultyData'][difficulty]['Victory']
                AllDiff['Defeat'] += analysis['DifficultyData'][difficulty]['Defeat']

        AllDiff['Winrate'] = f"{100*AllDiff['Victory']/(AllDiff['Victory'] + AllDiff['Defeat']):.0f}%" if (AllDiff['Victory'] +
                                                                                                           AllDiff['Defeat']) > 0 else '-'

        self.stats_difficulty_UI_dict['All'] = MUI.DifficultyEntry('Σ',
                                                                   AllDiff['Victory'],
                                                                   AllDiff['Defeat'],
                                                                   AllDiff['Winrate'],
                                                                   50,
                                                                   idx * 18 + 23,
                                                                   parent=self.TAB_DifficultyRegions)

        # Region stats
        for item in set(self.stats_region_UI_dict.keys()):
            self.stats_region_UI_dict[item].deleteLater()
            del self.stats_region_UI_dict[item]

        for idx, region in enumerate(analysis['RegionData']):
            self.stats_region_UI_dict[region] = MUI.RegionStats(region,
                                                                analysis['RegionData'][region],
                                                                20 + idx * 18,
                                                                bg=True if idx % 2 else False,
                                                                parent=self.TAB_DifficultyRegions)

        ### Commander stats
        self.my_commander_analysis = analysis['CommanderData']
        self.my_commander_sort_update()

        ### Ally commander stats
        self.ally_commander_analysis = analysis['AllyCommanderData']
        self.ally_commander_sort_update()

        ### Unit stats
        if self.p.CAnalysis.full_analysis_finished:
            self.update_unit_stats(analysis['UnitData'])

    def update_unit_stats(self, unit_data):
        """ Update unit stats """

        # Create tab if it's not there yey
        if not hasattr(self, 'TAB_CommUnitStats'):
            self.TAB_CommUnitStats = QtWidgets.QWidget()
            self.TABW_StatResults.insertTab(4, self.TAB_CommUnitStats, "Unit stats")

        # Update commander units widget
        if not hasattr(self, 'WD_unit_stats'):
            self.WD_unit_stats = MUI.UnitStats(unit_data, parent=self.TAB_CommUnitStats)
        else:
            self.WD_unit_stats.unit_data = unit_data
            self.WD_unit_stats.update_units()

        # Amon unit tab
        if not hasattr(self, 'TAB_AmonUnitStats'):
            self.TAB_AmonUnitStats = QtWidgets.QWidget()
            self.TABW_StatResults.insertTab(5, self.TAB_AmonUnitStats, "Amon stats")

        # Update amon units widget
        if not hasattr(self, 'WD_amon_unit_stats'):
            self.WD_amon_unit_stats = MUI.AmonUnitStats(unit_data['amon'], parent=self.TAB_AmonUnitStats)
        else:
            self.WD_amon_unit_stats.update_data(unit_data['amon'])

    def switched_tab(self, idx):
        """ Updating bg depends whether a unit is visible, this break when switched to another tab.
        This function updates background for Amon's units when you switch to the tab"""
        if idx == 5:
            self.WD_amon_unit_stats.update_backgrounds()

    def my_commander_sort_update(self):
        """ Creates and updates widgets for my commander stats """
        sort_my_commanders_by = self.MyCommanderComboBox.currentText()
        translate = {
            'APM': 'MedianAPM',
            'Winrate': 'Winrate',
            'Losses': 'Defeat',
            'Wins': 'Victory',
            'Frequency': 'Frequency',
            'Kills': 'KillFraction'
        }
        self.my_commander_analysis = {
            k: v
            for k, v in sorted(self.my_commander_analysis.items(), key=lambda x: x[1][translate[sort_my_commanders_by]], reverse=True)
        }

        for item in set(self.stats_mycommander_UI_dict.keys()):
            self.stats_mycommander_UI_dict[item].deleteLater()
            del self.stats_mycommander_UI_dict[item]

        idx = 0
        spacing = 21
        firstCommander = None
        for co in self.my_commander_analysis:
            if co == 'any':
                continue
            if firstCommander is None:
                firstCommander = co
            self.stats_mycommander_UI_dict[co] = MUI.CommanderEntry(co,
                                                                    f"{100*self.my_commander_analysis[co]['Frequency']:.1f}%",
                                                                    self.my_commander_analysis[co]['Victory'],
                                                                    self.my_commander_analysis[co]['Defeat'],
                                                                    f"{100*self.my_commander_analysis[co]['Winrate']:.0f}%",
                                                                    f"{self.my_commander_analysis[co]['MedianAPM']:.0f}",
                                                                    f"{100*self.my_commander_analysis[co].get('KillFraction',0):.0f}%",
                                                                    idx * spacing + 23,
                                                                    parent=self.TAB_MyCommanders,
                                                                    bg=True if idx % 2 == 1 else False)

            self.stats_mycommander_UI_dict[co].bt_button.clicked.connect(partial(self.detailed_my_commander_stats_update, co))
            idx += 1

        self.stats_mycommander_UI_dict['any'] = MUI.CommanderEntry('Σ',
                                                                   f"{100*self.my_commander_analysis['any']['Frequency']:.0f}%",
                                                                   self.my_commander_analysis['any']['Victory'],
                                                                   self.my_commander_analysis['any']['Defeat'],
                                                                   f"{100*self.my_commander_analysis['any']['Winrate']:.0f}%",
                                                                   f"{self.my_commander_analysis['any']['MedianAPM']:.0f}",
                                                                   f"{100*self.my_commander_analysis['any'].get('KillFraction',0):.0f}%",
                                                                   idx * spacing + 23,
                                                                   parent=self.TAB_MyCommanders,
                                                                   button=False)

        # Update details
        if hasattr(self, 'my_detailed_info') and self.my_detailed_info is not None:
            self.my_detailed_info.deleteLater()
            self.my_detailed_info = None

        if hasattr(self, 'my_commander_clicked') and self.my_commander_clicked in self.my_commander_analysis:
            self.my_detailed_info = MUI.CommanderStats(self.my_commander_clicked, self.my_commander_analysis, parent=self.TAB_MyCommanders)
        elif len(self.my_commander_analysis) > 1:
            self.my_detailed_info = MUI.CommanderStats(firstCommander, self.my_commander_analysis, parent=self.TAB_MyCommanders)

    def detailed_my_commander_stats_update(self, commander):
        """ Updates my commander details"""
        self.my_commander_clicked = commander
        if hasattr(self, 'my_detailed_info') and self.my_detailed_info is not None:
            self.my_detailed_info.deleteLater()
            self.my_detailed_info = None
        self.my_detailed_info = MUI.CommanderStats(commander, self.my_commander_analysis, parent=self.TAB_MyCommanders)

    def ally_commander_sort_update(self):
        """ Creates and updates widgets for allu commander stats """
        sort_commanders_by = self.AllyCommanderComboBox.currentText()
        translate = {
            'APM': 'MedianAPM',
            'Winrate': 'Winrate',
            'Losses': 'Defeat',
            'Wins': 'Victory',
            'Frequency': 'Frequency',
            'Kills': 'KillFraction'
        }
        self.ally_commander_analysis = {
            k: v
            for k, v in sorted(self.ally_commander_analysis.items(), key=lambda x: x[1][translate[sort_commanders_by]], reverse=True)
        }

        for item in set(self.stats_allycommander_UI_dict.keys()):
            self.stats_allycommander_UI_dict[item].deleteLater()
            del self.stats_allycommander_UI_dict[item]

        idx = 0
        spacing = 21
        firstCommander = None
        for co in self.ally_commander_analysis:
            if co == 'any':
                continue
            if firstCommander is None:
                firstCommander = co
            self.stats_allycommander_UI_dict[co] = MUI.CommanderEntry(co,
                                                                      f"{100*self.ally_commander_analysis[co]['Frequency']:.1f}%",
                                                                      self.ally_commander_analysis[co]['Victory'],
                                                                      self.ally_commander_analysis[co]['Defeat'],
                                                                      f"{100*self.ally_commander_analysis[co]['Winrate']:.0f}%",
                                                                      f"{self.ally_commander_analysis[co]['MedianAPM']:.0f}",
                                                                      f"{100*self.ally_commander_analysis[co].get('KillFraction',0):.0f}%",
                                                                      idx * spacing + 23,
                                                                      parent=self.TAB_AlliedCommanders,
                                                                      bg=True if idx % 2 == 1 else False)

            self.stats_allycommander_UI_dict[co].bt_button.clicked.connect(partial(self.detailed_ally_commander_stats_update, co))
            idx += 1

        self.stats_allycommander_UI_dict['any'] = MUI.CommanderEntry('Σ',
                                                                     f"{100*self.ally_commander_analysis['any']['Frequency']:.0f}%",
                                                                     self.ally_commander_analysis['any']['Victory'],
                                                                     self.ally_commander_analysis['any']['Defeat'],
                                                                     f"{100*self.ally_commander_analysis['any']['Winrate']:.0f}%",
                                                                     f"{self.ally_commander_analysis['any']['MedianAPM']:.0f}",
                                                                     f"{100*self.ally_commander_analysis['any'].get('KillFraction',0):.0f}%",
                                                                     idx * spacing + 23,
                                                                     parent=self.TAB_AlliedCommanders,
                                                                     button=False)

        # Update details
        if hasattr(self, 'ally_detailed_info') and self.ally_detailed_info is not None:
            self.ally_detailed_info.deleteLater()
            self.ally_detailed_info = None

        if hasattr(self, 'ally_commander_clicked') and self.ally_commander_clicked in self.ally_commander_analysis:
            self.ally_detailed_info = MUI.CommanderStats(self.ally_commander_clicked, self.ally_commander_analysis, parent=self.TAB_AlliedCommanders)
        elif len(self.ally_commander_analysis) > 1:
            self.ally_detailed_info = MUI.CommanderStats(firstCommander, self.ally_commander_analysis, parent=self.TAB_AlliedCommanders)

    def detailed_ally_commander_stats_update(self, commander):
        """ Updates allied commander details"""
        self.ally_commander_clicked = commander
        if hasattr(self, 'ally_detailed_info') and self.ally_detailed_info is not None:
            self.ally_detailed_info.deleteLater()
            self.ally_detailed_info = None
        self.ally_detailed_info = MUI.CommanderStats(commander, self.ally_commander_analysis, parent=self.TAB_AlliedCommanders)

    def map_link_update(self, mapname=None, fdict=None):
        """ Updates the fastest map to clicked map """
        if len(fdict) <= 1:
            self.QB_FastestMap.hide()
        else:
            self.QB_FastestMap.update_data(mapname, fdict, self.p.CAnalysis.main_handles)
            self.last_fastest_map = mapname