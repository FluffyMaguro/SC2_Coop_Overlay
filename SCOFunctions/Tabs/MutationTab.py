from functools import partial
from PyQt5 import QtCore, QtGui, QtWidgets
from SCOFunctions.MTheming import MColors
from SCOFunctions.MUserInterface import Cline, SortingQLabel
from SCOFunctions.SC2Dictionaries import weekly_mutations


class MutationWidget(QtWidgets.QWidget):
    def __init__(self, mutation_name: str, mutation_data, bg: bool = False):
        super().__init__()

        height = 22
        self.setGeometry(QtCore.QRect(0, 0, 931, 22))
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        if bg:
            self.bg = QtWidgets.QFrame(self)
            self.bg.setGeometry(QtCore.QRect(5, 0, 921, height + 1))
            self.bg.setAutoFillBackground(True)
            self.bg.setBackgroundRole(QtGui.QPalette.AlternateBase)

        self.name = QtWidgets.QLabel(mutation_name, self)
        self.name.setGeometry(QtCore.QRect(10, 0, 200, 20))

        self.map = QtWidgets.QLabel(mutation_data['map'], self)
        self.map.setGeometry(QtCore.QRect(200, 0, 200, 20))

        self.difficulty = QtWidgets.QLabel("None", self)
        self.difficulty.setGeometry(QtCore.QRect(350, 0, 100, 20))

        self.mutators = QtWidgets.QLabel('   |   '.join(mutation_data['mutators']), self)
        self.mutators.setGeometry(QtCore.QRect(420, 0, 600, 20))

    def set_difficulty(self, difficulty: str):
        """ Updates the difficulty"""
        self.difficulty.setText(difficulty)
        if difficulty == "Brutal":
            self.setStyleSheet(f"color: {MColors.game_weekly}")
        elif difficulty != "None":
            self.setStyleSheet(f"color: {MColors.player_highlight}")
        else:
            self.setStyleSheet("")


class MutationTab(QtWidgets.QWidget):
    def __init__(self, TabWidget):
        super().__init__()
        self.p = self
        self.mutations = dict()

        # Labels
        offset = 10
        self.name = SortingQLabel(self)
        self.name.setText("Mutation")
        self.name.setGeometry(QtCore.QRect(offset + 10, 0, 200, 20))
        self.name.setAlignment(QtCore.Qt.AlignLeft)
        self.name.activate()
        self.name.clicked.connect(partial(self.sort_mutations, self.name))

        self.map = SortingQLabel(self)
        self.map.setText("Map")
        self.map.setAlignment(QtCore.Qt.AlignLeft)
        self.map.setGeometry(QtCore.QRect(offset + 200, 0, 200, 20))
        self.map.clicked.connect(partial(self.sort_mutations, self.map))

        self.difficulty = SortingQLabel(self)
        self.difficulty.setText("Difficulty")
        self.difficulty.setToolTip("Maximum difficulty the mutation was completed on")
        self.difficulty.setAlignment(QtCore.Qt.AlignLeft)
        self.difficulty.setGeometry(QtCore.QRect(offset + 350, 0, 100, 20))
        self.difficulty.clicked.connect(partial(self.sort_mutations, self.difficulty))

        self.mutators = QtWidgets.QLabel("Mutators", self)
        self.mutators.setAlignment(QtCore.Qt.AlignLeft)
        self.mutators.setGeometry(QtCore.QRect(offset + 420, 0, 600, 20))

        self.line = Cline(self)
        self.line.setGeometry(QtCore.QRect(5, 22, 941, 1))

        for item in (self.name, self.map, self.difficulty, self.mutators):
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
            widget.set_difficulty(weekly_data[mutation])

    def sort_mutations(self, caller):
        caller.activate()

        sort_by = SortingQLabel.active[self].value
        reverse = SortingQLabel.active[self].reverse
