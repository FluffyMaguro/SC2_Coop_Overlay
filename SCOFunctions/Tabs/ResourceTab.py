from PyQt5 import QtWidgets, QtGui, QtCore
import SCOFunctions.MUserInterface as MUI


class ResourceTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.p = parent

        # Performance group box
        self.gb_Resources = QtWidgets.QFrame(self)
        self.gb_Resources.setAutoFillBackground(True)
        self.gb_Resources.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.gb_Resources.setFrameShadow(QtWidgets.QFrame.Plain)
        self.gb_Resources.setGeometry(QtCore.QRect(15, 15, 550, 310))

        # Performance description
        self.la_performance_description = QtWidgets.QLabel(self.gb_Resources)
        self.la_performance_description.setGeometry(QtCore.QRect(14, 10, self.gb_Resources.width() - 20, 300))
        self.la_performance_description.setAlignment(QtCore.Qt.AlignTop)
        self.la_performance_description.setText(
            '<b>Performance overlay:</b><br><br>Shows performance overlay with CPU/RAM/Disk/Network usage for system and StarCraft II.\
                                                <br><br><b>Read</b> and <b>Write</b> stats are disk usage of StarCraft II (current & total).\
                                                <br><b>CPUc</b> is per core CPU usage. 100% means one core fully used.')
        self.la_performance_description.setWordWrap(True)

        # Checks whether to show/hide
        self.ch_performance_show = QtWidgets.QCheckBox(self.gb_Resources)
        self.ch_performance_show.setGeometry(QtCore.QRect(14, 125, 200, 17))
        self.ch_performance_show.setText('Show performance overlay')
        self.ch_performance_show.clicked.connect(self.p.show_hide_performance_overlay)

        # Position overlay
        self.bt_performance_overlay_position = QtWidgets.QPushButton(self.gb_Resources)
        self.bt_performance_overlay_position.setGeometry(QtCore.QRect(14, 150, 150, 25))
        self.bt_performance_overlay_position.setText('Change overlay position')
        self.bt_performance_overlay_position.clicked.connect(self.p.update_performance_overlay_position)

        # Hotkey description
        self.la_hotkey_performance_desc = QtWidgets.QLabel(self.gb_Resources)
        self.la_hotkey_performance_desc.setGeometry(QtCore.QRect(15, 220, 300, 20))
        self.la_hotkey_performance_desc.setText('<b>Hotkey for showing/hiding overlay</b>')

        # Hotkey
        self.KEY_Performance = MUI.CustomKeySequenceEdit(self.gb_Resources)
        self.KEY_Performance.setGeometry(QtCore.QRect(15, 245, 113, 25))
        self.KEY_Performance.setToolTip('Key for showing or hiding performance overlay')
        self.KEY_Performance.keySequenceChanged.connect(self.p.hotkey_changed)

        # Apply
        self.bt_performance_apply = QtWidgets.QPushButton(self.gb_Resources)
        self.bt_performance_apply.setGeometry(QtCore.QRect(150, 245, 75, 25))
        self.bt_performance_apply.setText('Apply')
        self.bt_performance_apply.clicked.connect(self.p.saveSettings)