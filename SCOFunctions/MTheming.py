from dataclasses import dataclass
from PyQt5 import QtCore, QtGui, QtWidgets


@dataclass
class Colors:
    """ Dataclass for colors used in the app.
    It's separate from a palette used by PyQt5 """
    
    msg = "#555"
    msg_success = "green"
    msg_failure = 'red'
    chat_main = '#55f'
    chat_other = '#558F22'
    player_highlight = "#55f"


MColors = Colors()


def set_dark_theme(main, app, tab, version):
    MColors.msg = "#ccc"
    MColors.msg_success = '#4f4'
    MColors.msg_failure = '#f44'
    MColors.chat_main = '#6587FF'
    MColors.chat_other = '#20DE49'
    MColors.player_highlight = '#77f'

    DARK0 = QtGui.QColor(33, 33, 33)
    DARK1 = QtGui.QColor(55, 55, 55)
    ALT = QtGui.QColor(88, 88, 88)
    LINK = QtGui.QColor(200, 200, 200)
    ORG = QtGui.QColor(255, 125, 0)

    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)

    dark_palette.setColor(QtGui.QPalette.Button, DARK1)
    dark_palette.setColor(QtGui.QPalette.Background, DARK1)  # far background
    dark_palette.setColor(QtGui.QPalette.Base, DARK0)  # bg of checkboxes, edit fields

    dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)

    dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    dark_palette.setColor(QtGui.QPalette.Highlight, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    dark_palette.setColor(QtGui.QPalette.AlternateBase, ALT)
    dark_palette.setColor(QtGui.QPalette.Link, LINK)

    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtCore.Qt.darkGray)
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Foreground, QtCore.Qt.darkGray)
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtCore.Qt.darkGray)

    app.setStyle('Fusion')
    app.setPalette(dark_palette)

    # Remove title bar because it cannot by stylized
    tab.dark_mode_active = True
    tab.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
    tab.show()

    # Update title and show new button
    tab.title_bar.new_title.setText(f"StarCraft Co-op Overlay (v{str(version)[0]}.{str(version)[1:]})")
    tab.title_bar.show()

    # Small tweaks
    main.TAB_Games.WD_RecentGamesHeading.setStyleSheet('background-color: #454545; font-weight: bold')
    main.TAB_Games.GameTabLine.setStyleSheet('background-color: #777')
    main.TAB_Games.ed_games_search.setStyleSheet('background-color: #333; font-weight: normal')

    main.TAB_Players.WD_WinratesHeading.setStyleSheet("QWidget {background-color: #454545; font-weight: bold}")
    main.TAB_Players.FR_Winrate_Controls.setStyleSheet('background-color: #454545')
    main.TAB_Players.PlayerTabLine.setStyleSheet('background-color: #777')
    main.TAB_Players.ED_Winrate_Search.setStyleSheet('background-color: #333')

    main.TAB_Randomizer.BT_RNG_Description.setEnabled(True)
    main.TAB_Stats.LA_GamesFound.setEnabled(True)
    main.TAB_Stats.LA_IdentifiedPlayers.setEnabled(True)

    tab.setStyleSheet(
        "QScrollArea > QWidget > QWidget {background: #454545}"
        "QPushButton {background: #454545}"
        "QScrollArea QLineEdit {background: #333}"
        ) 