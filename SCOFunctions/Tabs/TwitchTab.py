import os
from PyQt5 import QtWidgets, QtGui, QtCore
import SCOFunctions.MUserInterface as MUI
import SCOFunctions.HelperFunctions as HF
from SCOFunctions.Settings import Setting_manager as SM


class TwitchTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.p = parent
        self.bank_found_locations = set()

        self.qb_twitch_text = QtWidgets.QFrame(self)
        self.qb_twitch_text.setAutoFillBackground(True)
        self.qb_twitch_text.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.qb_twitch_text.setFrameShadow(QtWidgets.QFrame.Plain)
        self.qb_twitch_text.setGeometry(QtCore.QRect(15, 15, 550, 380 if HF.isWindows() else 555))

        self.la_twitch_text = QtWidgets.QLabel(self.qb_twitch_text)
        self.la_twitch_text.setWordWrap(True)
        self.la_twitch_text.setGeometry(QtCore.QRect(15, 10, 530, 700))
        self.la_twitch_text.setAlignment(QtCore.Qt.AlignTop)
        self.la_twitch_text.setOpenExternalLinks(True)
        self.la_twitch_text.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.la_twitch_text.setText(
            """<b>About the twitch bot:</b><br><br>This is a feature for twitch streamers. First, it lets you overlay stream chat on your screen. \
                                    Second, it connects the twitch chat to the StarCraft II game when playing one of my [MM] maps. \
                                    Viewers can spawn units, enemy waves, give resources, enable/disable mutators or join as a unit.<br> 
                                    <br> 
                                    This panel provides only the most basic control over the bot. Creating a new bot is not neccesary, \
                                        but you can do so and fill its name and oauth in the Setting.json.
                                    <br><br><br>
                                    <u><b>Commands for the streamer:</b></u>
                                    <br><br>
                                    <b>!gm full</b> | <b>!gm stop</b> | <b>!gm</b></li><br> → Sets the level to of integration to full, none, \
                                        or just messages and joins (not affecting gameplay!)<br><br>
                                    <b>!cooldown X</b><br>→ Sets the cooldown on commands to X seconds per viewer (default cooldown is 30s)
                                    <br><br>
                                    <u><b>Commands for the viewers:</b></u>
                                    <br>
                                    <br><b>!join X</b>→ Join as a random unit for player X
                                    <br><b>!message X</b>→ Send a message X to the game
                                    <br><b>!spawn X Y Z</b>→ spawn Y units of type X for player Z (+rand → at random position)
                                    <br><b>!mutator X</b>→ enables mutator X (+disable → disables)
                                    <br><b>!resources X Y Z</b>→ Adds X minerals and Y vespene to player Z
                                    <br><b>!wave X Y</b>→ Spawns an enemy wave of tech X and size Y
                                    """)

        self.la_twitch_channel_name = QtWidgets.QLabel(self)
        self.la_twitch_channel_name.setGeometry(QtCore.QRect(601, 25, 300, 20))
        self.la_twitch_channel_name.setText("Use only for your own channel!")

        self.ED_twitch_channel_name = QtWidgets.QLineEdit(self)
        self.ED_twitch_channel_name.setGeometry(QtCore.QRect(601, 50, 140, 20))
        self.ED_twitch_channel_name.setAlignment(QtCore.Qt.AlignCenter)
        self.ED_twitch_channel_name.setPlaceholderText("channel name")

        self.bt_twitch = QtWidgets.QPushButton(self)
        self.bt_twitch.setGeometry(QtCore.QRect(600, 110, 140, 25))
        self.bt_twitch.setText('Run the bot')
        self.bt_twitch.clicked.connect(self.p.start_stop_bot)

        self.ch_twitch = QtWidgets.QCheckBox(self)
        self.ch_twitch.setGeometry(QtCore.QRect(601, 140, 200, 17))
        self.ch_twitch.setText('Start the bot automatically')

        self.bt_twitch_position = QtWidgets.QPushButton(self)
        self.bt_twitch_position.setGeometry(QtCore.QRect(600, 190, 140, 25))
        self.bt_twitch_position.setText('Change chat position')
        self.bt_twitch_position.clicked.connect(self.p.update_twitch_chat_position)

        self.ch_twitch_chat = QtWidgets.QCheckBox(self)
        self.ch_twitch_chat.setGeometry(QtCore.QRect(601, 220, 200, 17))
        self.ch_twitch_chat.setText('Show chat as overlay')
        self.ch_twitch_chat.clicked.connect(self.p.create_twitch_chat)

        self.la_twitch_bank_desc = QtWidgets.QLabel(self)
        self.la_twitch_bank_desc.setGeometry(QtCore.QRect(22, 420, 800, 20))
        self.la_twitch_bank_desc.setText(
            "Choose bank location. It's different for every account and server. At start the app will try to find the correct bank.")

        # Bank combo-box
        self.CB_twitch_banks = QtWidgets.QComboBox(self)
        self.CB_twitch_banks.setGeometry(QtCore.QRect(20, 443, 800, 20))
        self.CB_twitch_banks.setEnabled(False)

        # Refresh button
        self.BT_find_banks = QtWidgets.QPushButton(self)
        self.BT_find_banks.setGeometry(QtCore.QRect(830, 440, 100, 25))
        self.BT_find_banks.setText('Refresh')
        self.BT_find_banks.clicked.connect(self.find_and_update_banks)

        # Info label
        self.LA_InfoTwitch = QtWidgets.QLabel(self)
        self.LA_InfoTwitch.setGeometry(QtCore.QRect(20, 560, 700, 20))
        self.LA_InfoTwitch.setStyleSheet('color: red')

    def find_and_update_banks(self):
        """ Finds banks, update UI """
        folder = os.path.dirname(SM.settings['account_folder'])

        for root, _, files in os.walk(folder):
            for file in files:
                if file == 'MMTwitchIntegration.SC2Bank':
                    path = os.path.join(root, file)
                    if not path in self.bank_found_locations:
                        self.CB_twitch_banks.addItem(path)
                        self.bank_found_locations.add(path)

    def change_bank_names(self, CAnalysis):
        """ Changes bank names and returns a dictionary of name: path"""
        out = dict()
        for i in range(self.CB_twitch_banks.count()):
            bank_path = self.CB_twitch_banks.itemText(i)
            for handle in CAnalysis.name_handle_dict:
                if handle in bank_path:
                    if '1-S2-' in bank_path:
                        region = 'NA'
                    elif '2-S2-' in bank_path:
                        region = 'EU'
                    elif '3-S2-' in bank_path:
                        region = 'KR'
                    elif '5-S2-' in bank_path:
                        region = 'CN'
                    elif '98-S2-' in bank_path:
                        region = 'PTR'
                    else:
                        region = '?'

                    text = f"{CAnalysis.name_handle_dict[handle]} ({region}) - {bank_path}"
                    out[text] = bank_path
                    self.CB_twitch_banks.setItemText(i, text)
                    break

        return out