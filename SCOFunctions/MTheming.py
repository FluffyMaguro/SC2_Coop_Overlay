from PyQt5 import QtCore, QtGui, QtWidgets

MGS_COLOR = "#555"


def get_msg_color():
    return MGS_COLOR


def set_dark_theme(main, app, tab, version):
    global MGS_COLOR
    MGS_COLOR = "#FFF"

    DARK0 = QtGui.QColor(33, 33, 33)
    DARK1 = QtGui.QColor(53, 53, 53)
    DARK2 = QtGui.QColor(67, 67, 67)
    DARK3 = QtGui.QColor(88, 88, 88)
    LINK = QtGui.QColor(255, 255, 255)
    ORG = QtGui.QColor(255, 125, 0)

    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)

    dark_palette.setColor(QtGui.QPalette.Window, DARK2)  # not here
    dark_palette.setColor(QtGui.QPalette.Button, DARK1)
    dark_palette.setColor(QtGui.QPalette.Background, DARK1)  # far background
    dark_palette.setColor(QtGui.QPalette.Base, DARK0)  # bg of checkboxes, edit fields

    dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)

    dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    dark_palette.setColor(QtGui.QPalette.Highlight, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    dark_palette.setColor(QtGui.QPalette.AlternateBase, DARK3)
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
    main.WD_RecentGamesHeading.setStyleSheet('background-color: #434343; font-weight: bold')
    main.WD_WinratesHeading.setStyleSheet('background-color: #434343; font-weight: bold')
    main.FR_Winrate_Controls.setStyleSheet('background-color: #434343')
    main.GameTabLine.setStyleSheet('background-color: #777')
    main.PlayerTabLine.setStyleSheet('background-color: #777')
    main.ed_games_search.setStyleSheet('background-color: #333; font-weight: normal')
    main.ED_Winrate_Search.setStyleSheet('background-color: #333')

    tab.setStyleSheet(
        "QScrollArea > QWidget > QWidget {background: #434343}"
        "QScrollArea QPushButton {background: #464646}"
        "QScrollArea QLineEdit {background: #333}"
        ) 