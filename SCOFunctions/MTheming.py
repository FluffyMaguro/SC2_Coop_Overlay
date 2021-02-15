from PyQt5 import QtCore, QtGui, QtWidgets

MGS_COLOR = "#555"


def get_msg_color():
    return MGS_COLOR


def set_dark_theme(main, app, tab, version):
    global MGS_COLOR
    MGS_COLOR = "#FFF"

    DBG = QtGui.QColor(33, 33, 33)
    BG = QtGui.QColor(53, 53, 53)
    ALT = QtGui.QColor(88, 88, 88)
    LINK = QtGui.QColor(255, 255, 255)
    ORG = QtGui.QColor(255, 125, 0)

    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)

    dark_palette.setColor(QtGui.QPalette.Window, BG)  # not here
    dark_palette.setColor(QtGui.QPalette.Button, BG)
    dark_palette.setColor(QtGui.QPalette.Background, BG)  # far background
    dark_palette.setColor(QtGui.QPalette.Base, DBG)  # bg of checkboxes, edit fields

    dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)

    dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(0, 255, 0).lighter())
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