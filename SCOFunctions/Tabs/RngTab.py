import os
from PyQt5 import QtWidgets, QtGui, QtCore

import SCOFunctions.MUserInterface as MUI
import SCOFunctions.MainFunctions as MF
from SCOFunctions.MRandomizer import randomize
from SCOFunctions.MFilePath import truePath
from SCOFunctions.SC2Dictionaries import prestige_names, CommanderMastery
from SCOFunctions.MLogging import Logger

logger = Logger('RNG', Logger.levels.INFO)


class RngTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.p = parent

        # Generate button
        self.BT_RNG_Generate = QtWidgets.QPushButton(self)
        self.BT_RNG_Generate.setGeometry(QtCore.QRect(720, 90, 150, 40))
        self.BT_RNG_Generate.setText('Generate')
        self.BT_RNG_Generate.clicked.connect(self.randomize_commander)

        # Description
        self.BT_RNG_Description = QtWidgets.QLabel(self)
        self.BT_RNG_Description.setGeometry(QtCore.QRect(370, 20, 510, 60))
        self.BT_RNG_Description.setWordWrap(True)
        self.BT_RNG_Description.setEnabled(False)
        self.BT_RNG_Description.setText('This commander randomizer randomly chooses a combination of commander, prestige and masteries.\
                                        <br>Specify which commanders and prestiges can be picked. Mastery points will be randomized with\
                                        either all points into one mastery choice, fully random or not at all.')

        # Mastery label
        self.CB_RNG_Mastery_Label = QtWidgets.QLabel(self)
        self.CB_RNG_Mastery_Label.setGeometry(QtCore.QRect(370, 80, 200, 20))
        self.CB_RNG_Mastery_Label.setText('<b>Mastery</b>')

        # Mastery combo-box
        self.CB_RNG_Mastery = QtWidgets.QComboBox(self)
        self.CB_RNG_Mastery.setGeometry(QtCore.QRect(370, 100, 140, 21))
        self.CB_RNG_Mastery.addItem('All points into one')
        self.CB_RNG_Mastery.addItem('Fully random mastery')
        self.CB_RNG_Mastery.addItem('No mastery generated')

        # Map
        self.CB_RNG_Map = QtWidgets.QCheckBox(self)
        self.CB_RNG_Map.setGeometry(QtCore.QRect(530, 85, 140, 21))
        self.CB_RNG_Map.setChecked(True)
        self.CB_RNG_Map.setText('Random map')

        # Race
        self.CB_RNG_Race = QtWidgets.QCheckBox(self)
        self.CB_RNG_Race.setGeometry(QtCore.QRect(530, 105, 140, 21))
        self.CB_RNG_Race.setChecked(True)
        self.CB_RNG_Race.setText('Random enemy race')

        ### Commanders & prestiges
        self.FR_RNG_GB = QtWidgets.QFrame(self)
        self.FR_RNG_GB.setAutoFillBackground(True)
        self.FR_RNG_GB.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_RNG_GB.setFrameShadow(QtWidgets.QFrame.Plain)
        self.FR_RNG_GB.setGeometry(QtCore.QRect(15, 15, 280, 455))

        self.RNG_co_desc = QtWidgets.QLabel(self.FR_RNG_GB)
        self.RNG_co_desc.setGeometry(QtCore.QRect(0, 5, 280, 20))
        self.RNG_co_desc.setAlignment(QtCore.Qt.AlignCenter)
        self.RNG_co_desc.setText('Choose commanders and prestiges')

        self.FR_RNG_Commanders = QtWidgets.QFrame(self.FR_RNG_GB)
        self.FR_RNG_Commanders.setGeometry(QtCore.QRect(35, 35, 260, 400))
        self.FR_RNG_Commanders.show()

        # Heading
        self.RNG_co_heading = QtWidgets.QLabel(self.FR_RNG_Commanders)
        self.RNG_co_heading.setGeometry(QtCore.QRect(0, 5, 200, 20))
        self.RNG_co_heading.setText('<b>Commander</b>')

        self.RNG_co_heading_prestige = QtWidgets.QLabel(self.FR_RNG_Commanders)
        self.RNG_co_heading_prestige.setGeometry(QtCore.QRect(100, 5, 110, 20))
        self.RNG_co_heading_prestige.setAlignment(QtCore.Qt.AlignCenter)
        self.RNG_co_heading_prestige.setText('<b>Prestige</b>')

        self.RNG_co_dict = dict()
        for prest in {0, 1, 2, 3}:
            self.RNG_co_dict[('heading', prest)] = QtWidgets.QLabel(self.FR_RNG_Commanders)
            self.RNG_co_dict[('heading', prest)].setGeometry(QtCore.QRect(104 + prest * 30, 24, 300, 20))
            self.RNG_co_dict[('heading', prest)].setText(str(prest))

        # Fill commanders
        for idx, co in enumerate(prestige_names):
            self.RNG_co_dict[(co, 'label')] = QtWidgets.QLabel(self.FR_RNG_Commanders)
            self.RNG_co_dict[(co, 'label')].setGeometry(QtCore.QRect(0, 40 + 20 * idx, 200, 20))
            self.RNG_co_dict[(co, 'label')].setText(co)

            for prest in {0, 1, 2, 3}:
                self.RNG_co_dict[(co, prest)] = QtWidgets.QCheckBox(self.FR_RNG_Commanders)
                self.RNG_co_dict[(co, prest)].setGeometry(QtCore.QRect(100 + prest * 30, 40 + 20 * idx, 50, 20))
                self.RNG_co_dict[(co, prest)].setToolTip(prestige_names[co][prest])
                if prest == 0:
                    self.RNG_co_dict[(co, prest)].setChecked(True)

        ### Result
        self.FR_RNG_Result = QtWidgets.QFrame(self)
        self.FR_RNG_Result.setGeometry(QtCore.QRect(370, 150, 500, 320))
        self.FR_RNG_Result.setAutoFillBackground(True)
        self.FR_RNG_Result.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_RNG_Result.setFrameShadow(QtWidgets.QFrame.Plain)

        # Background
        self.FR_RNG_Result_BG = QtWidgets.QLabel(self.FR_RNG_Result)
        self.FR_RNG_Result_BG.setGeometry(QtCore.QRect(0, 20, self.FR_RNG_Result.width(), 87))

        # Commander name
        self.FR_RNG_Result_CO = QtWidgets.QLabel(self.FR_RNG_Result)
        self.FR_RNG_Result_CO.setGeometry(QtCore.QRect(0, 20, self.FR_RNG_Result.width() - 20, 71))
        self.FR_RNG_Result_CO.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.FR_RNG_Result_CO.setStyleSheet(f'font-weight: bold; font-size: 30px; color: white;')
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(1)
        shadow.setOffset(2)
        self.FR_RNG_Result_CO.setGraphicsEffect(shadow)

        # Prestige
        self.FR_RNG_Result_Prestige = QtWidgets.QLabel(self.FR_RNG_Result)
        self.FR_RNG_Result_Prestige.setGeometry(QtCore.QRect(0, 43, self.FR_RNG_Result.width() - 20, 71))
        self.FR_RNG_Result_Prestige.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.FR_RNG_Result_Prestige.setStyleSheet('font-size: 13px; color: white')
        self.FR_RNG_Result_Prestige.setGraphicsEffect(shadow)

        self.FR_RNG_Result_Mastery = QtWidgets.QLabel(self.FR_RNG_Result)
        self.FR_RNG_Result_Mastery.setGeometry(QtCore.QRect(20, 90, 480, 200))
        self.FR_RNG_Result_Mastery.setStyleSheet('font-size: 13px')

        self.FR_RNG_Result_MapRace = QtWidgets.QLabel(self.FR_RNG_Result)
        self.FR_RNG_Result_MapRace.setGeometry(QtCore.QRect(10, 290, 480, 20))
        self.FR_RNG_Result_MapRace.setStyleSheet('font-size: 13px')
        self.FR_RNG_Result_MapRace.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        # Overlay checkbox
        self.FR_RNG_Overlay = QtWidgets.QCheckBox(self)
        self.FR_RNG_Overlay.setGeometry(QtCore.QRect(465, 480, 400, 17))
        self.FR_RNG_Overlay.setText('Show next random commander with prestige on the overlay')
        self.FR_RNG_Overlay.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.FR_RNG_Overlay.clicked.connect(self.RNG_Overlay_changed)

    def load_choices(self, choices):
        """ Loads choices from a setting file"""
        if len(choices) > 18:
            for co in prestige_names:
                for prest in {0, 1, 2, 3}:
                    self.RNG_co_dict[(co, prest)].setChecked(choices[f"{co}_{prest}"])

    def get_choices(self):
        out = dict()
        for co in prestige_names:
            for prest in {0, 1, 2, 3}:
                out[f"{co}_{prest}"] = self.RNG_co_dict[(co, prest)].isChecked()

        return out

    def RNG_Overlay_changed(self):
        self.p.saveSettings()
        if self.FR_RNG_Overlay.isChecked():
            self.randomize_commander()

    def randomize_commander(self):
        """ Randomizes commander based on current selection """

        # Get values
        mastery_all_in = True if self.CB_RNG_Mastery.currentText() == 'All points into one' else False
        commander_dict = dict()

        found = False
        for co in prestige_names:
            commander_dict[co] = set()
            for prest in {0, 1, 2, 3}:
                if self.RNG_co_dict[(co, prest)].isChecked():
                    commander_dict[co].add(prest)
                    found = True

        # Check if there are any prestiges selected
        if not found:
            logger.error('No commanders to randomize')
            return

        # Randomize
        commander, prestige, mastery, mmap, race = randomize(commander_dict, mastery_all_in=mastery_all_in)

        # Update image
        self.FR_RNG_Result_BG.setStyleSheet(f'background-color: black;')
        image_file = truePath(f'Layouts/Commanders/{commander}.png')
        if os.path.isfile(image_file):
            pixmap = QtGui.QPixmap(image_file)
            pixmap = pixmap.scaled(self.FR_RNG_Result_BG.width(), self.FR_RNG_Result_BG.height(), QtCore.Qt.KeepAspectRatio,
                                   QtCore.Qt.FastTransformation)
            self.FR_RNG_Result_BG.setPixmap(pixmap)

        # Commander and prestige
        self.FR_RNG_Result_CO.setText(commander)
        self.FR_RNG_Result_Prestige.setText(f"{prestige_names[commander][prestige]} (P{prestige})")

        # Mastery
        mastery = mastery if self.CB_RNG_Mastery.currentText() != 'No mastery generated' else [0, 0, 0, 0, 0, 0]
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

        MF.RNG_COMMANDER = {'Commander': commander, 'Prestige': prestige_names[commander][prestige]}