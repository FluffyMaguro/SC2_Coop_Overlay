from PyQt5 import QtCore, QtGui, QtWidgets
from SCOFunctions.MainFunctions import show_overlay
from SCOFunctions.MTheming import MColors
from SCOFunctions.MUserInterface import Cline, find_file
from SCOFunctions.SC2Dictionaries import weekly_mutations


class MutationWidget(QtWidgets.QWidget):
    def __init__(self, mutation_name: str, mutation_data, bg: bool):
        super().__init__()

        height = 22
        self.setGeometry(QtCore.QRect(0, 0, 931, 22))
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.files = []
        self.file_iter = 0
        self.last_type = None

        if bg:
            self.bg = QtWidgets.QFrame(self)
            self.bg.setGeometry(QtCore.QRect(5, 0, 921, height + 1))
            self.bg.setAutoFillBackground(True)
            self.bg.setBackgroundRole(QtGui.QPalette.AlternateBase)

        self.name = QtWidgets.QLabel(mutation_name, self)
        self.name.setGeometry(QtCore.QRect(10, 0, 200, 20))

        self.map = QtWidgets.QLabel(mutation_data['map'], self)
        self.map.setGeometry(QtCore.QRect(200, 0, 200, 20))

        self.winloss = QtWidgets.QLabel(self)
        self.winloss.setGeometry(QtCore.QRect(305, 0, 80, 20))
        self.winloss.setAlignment(QtCore.Qt.AlignCenter)

        self.difficulty = QtWidgets.QLabel("None", self)
        self.difficulty.setGeometry(QtCore.QRect(345, 0, 100, 20))
        self.difficulty.setAlignment(QtCore.Qt.AlignCenter)

        self.mutators = QtWidgets.QLabel('   |   '.join(mutation_data['mutators']), self)
        self.mutators.setGeometry(QtCore.QRect(435, 0, 600, 20))

        self.overlay_btn = QtWidgets.QPushButton("Overlays", self)
        self.overlay_btn.setGeometry(QtCore.QRect(811, 0, 55, 22))
        self.overlay_btn.clicked.connect(lambda: show_overlay(self.get_file(1)))
        self.overlay_btn.hide()

        self.file_btn = QtWidgets.QPushButton("Files", self)
        self.file_btn.setGeometry(QtCore.QRect(871, 0, 55, 22))
        self.file_btn.clicked.connect(lambda: find_file(self.get_file(2)))
        self.file_btn.hide()

    def get_file(self, type: int) -> str:
        """ Returns the next file to show"""

        # Move to another replay if we are clicking repeatedly
        if self.last_type == type:
            self.file_iter += 1
        else:
            self.last_type = type

        # The button is disabled if there are no files, no need to check for zero division
        self.file_iter %= len(self.files)
        return self.files[self.file_iter]

    def update(self, mutation):
        """ Updates the difficulty
        Args:
            mutation: dictionary containing information about difficulty, files, and W/L
        """
        # Files & buttons
        self.files = mutation['files']
        if self.files:
            self.overlay_btn.show()
            self.file_btn.show()

        # Win/loss
        self.winloss.setText(f"{mutation['wins']}/{mutation['losses']}")

        # Difficulty
        self.difficulty.setText(mutation['diff'])
        if mutation['diff'] == "Brutal":
            self.setStyleSheet(f"QLabel {{color: {MColors.game_weekly}}}")
        elif mutation['diff'] != "None":
            self.setStyleSheet(f"QLabel {{color: {MColors.player_highlight}}}")
        else:
            self.setStyleSheet("")


class MutationTab(QtWidgets.QWidget):
    def __init__(self, TabWidget):
        super().__init__()
        self.mutations = dict()

        # Labels
        offset = 10
        self.name = QtWidgets.QLabel("Mutation", self)
        self.name.setGeometry(QtCore.QRect(offset + 10, 0, 200, 20))

        self.map = QtWidgets.QLabel("Map", self)
        self.map.setGeometry(QtCore.QRect(offset + 200, 0, 200, 20))

        self.winloss = QtWidgets.QLabel("W/L", self)
        self.winloss.setToolTip("Win/Loss ratio")
        self.winloss.setGeometry(QtCore.QRect(offset + 305, 0, 80, 20))
        self.winloss.setAlignment(QtCore.Qt.AlignCenter)

        self.difficulty = QtWidgets.QLabel("Completed", self)
        self.difficulty.setToolTip("The highest difficulty the mutation was completed on")
        self.difficulty.setGeometry(QtCore.QRect(offset + 345, 0, 100, 20))
        self.difficulty.setAlignment(QtCore.Qt.AlignCenter)

        self.mutators = QtWidgets.QLabel("Mutators", self)
        self.mutators.setGeometry(QtCore.QRect(offset + 435, 0, 600, 20))

        self.line = Cline(self)
        self.line.setGeometry(QtCore.QRect(5, 22, 941, 1))

        for item in (self.name, self.map, self.winloss, self.difficulty, self.mutators):
            item.setStyleSheet("QLabel {font-weight: bold}")

        # Scroll
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setGeometry(QtCore.QRect(0, 23, TabWidget.frameGeometry().width() - 5, TabWidget.frameGeometry().height() - 50))
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area_content = QtWidgets.QWidget()
        self.scroll_area_content.setGeometry(QtCore.QRect(0, 0, 931, 561))

        self.scroll_area_contentLayout = QtWidgets.QVBoxLayout()
        self.scroll_area_contentLayout.setAlignment(QtCore.Qt.AlignTop)
        self.scroll_area_contentLayout.setContentsMargins(10, 0, 0, 0)

        # Finishing
        self.scroll_area_content.setLayout(self.scroll_area_contentLayout)
        self.scroll_area.setWidget(self.scroll_area_content)

        # Create mutations
        for iter, (mutation_name, mutation_data) in enumerate(weekly_mutations.items()):
            self.mutations[mutation_name] = MutationWidget(mutation_name, mutation_data, bool(iter % 2))
            self.scroll_area_contentLayout.addWidget(self.mutations[mutation_name])

    def update_data(self, weekly_data):
        for mutation, widget in self.mutations.items():
            widget.update(weekly_data[mutation])
