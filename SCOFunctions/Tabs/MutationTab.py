from functools import partial
from typing import Any, Dict

from PyQt5 import QtCore, QtGui, QtWidgets
from SCOFunctions.MainFunctions import show_overlay
from SCOFunctions.MTheming import MColors
from SCOFunctions.MUserInterface import Cline, SortingQLabel, find_file
from SCOFunctions.SC2Dictionaries import weekly_mutations


class MutationWidget(QtWidgets.QWidget):
    def __init__(self, mutation_name: str):
        super().__init__()
        self.data = dict()
        self.mutation_name = mutation_name

        height = 22
        self.setGeometry(QtCore.QRect(0, 0, 931, 22))
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.files = []
        self.file_iter = 0
        self.last_type = None

        self.bg = QtWidgets.QFrame(self)
        self.bg.setGeometry(QtCore.QRect(5, 0, 931, height + 1))
        self.bg.setAutoFillBackground(True)
        self.bg.setBackgroundRole(QtGui.QPalette.AlternateBase)
        self.bg.hide()

        self.name = QtWidgets.QLabel(mutation_name, self)
        self.name.setGeometry(QtCore.QRect(10, 0, 200, 20))

        self.map = QtWidgets.QLabel(weekly_mutations[mutation_name]['map'], self)
        self.map.setGeometry(QtCore.QRect(180, 0, 200, 20))

        self.wins = QtWidgets.QLabel(self)
        self.wins.setGeometry(QtCore.QRect(290, 0, 30, 20))
        self.wins.setAlignment(QtCore.Qt.AlignCenter)

        self.losses = QtWidgets.QLabel(self)
        self.losses.setGeometry(QtCore.QRect(310, 0, 30, 20))
        self.losses.setAlignment(QtCore.Qt.AlignCenter)

        self.winrate = QtWidgets.QLabel(self)
        self.winrate.setGeometry(QtCore.QRect(350, 0, 40, 20))
        self.winrate.setAlignment(QtCore.Qt.AlignCenter)

        self.difficulty = QtWidgets.QLabel("None", self)
        self.difficulty.setGeometry(QtCore.QRect(385, 0, 100, 20))
        self.difficulty.setAlignment(QtCore.Qt.AlignCenter)

        self.mutators = QtWidgets.QLabel('   |   '.join(weekly_mutations[mutation_name]['mutators']), self)
        self.mutators.setGeometry(QtCore.QRect(480, 0, 600, 20))

        self.overlay_btn = QtWidgets.QPushButton("Overlay", self)
        self.overlay_btn.setGeometry(QtCore.QRect(821, 0, 55, 22))

        self.overlay_btn.clicked.connect(lambda: show_overlay(self.get_file(1)))
        self.overlay_btn.hide()

        self.file_btn = QtWidgets.QPushButton("File", self)
        self.file_btn.setGeometry(QtCore.QRect(881, 0, 55, 22))

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

    def update(self, mutation: Dict[str, Any]):
        """ Updates the difficulty
        Args:
            mutation: dictionary containing information about difficulty, files, and W/L
        """
        self.data = mutation

        # Files & buttons
        self.files = mutation['files']
        if self.files:
            self.overlay_btn.show()
            self.file_btn.show()

        # Win/loss
        self.wins.setText(str(mutation['wins']))
        self.losses.setText(str(mutation['losses']))
        self.winrate.setText(f"{mutation['winrate']:.0%}")

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
        self.p = self
        self.weekly_mutations: Dict[str, Any] = dict()

        # Labels
        offset = 10

        self.name = SortingQLabel(self)
        self.name.setText("Mutation")
        self.name.setGeometry(QtCore.QRect(offset + 12, 4, 170, 20))
        self.name.setAlignment(QtCore.Qt.AlignLeft)
        self.name.activate()
        self.name.clicked.connect(partial(self.sort_mutations, self.name))

        self.map = SortingQLabel(self)
        self.map.setText("Map")
        self.map.setAlignment(QtCore.Qt.AlignLeft)
        self.map.setGeometry(QtCore.QRect(offset + 180, 4, 110, 20))
        self.map.clicked.connect(partial(self.sort_mutations, self.map))

        self.wins = SortingQLabel(self, True)
        self.wins.setText("W")
        self.wins.setAlignment(QtCore.Qt.AlignCenter)
        self.wins.setGeometry(QtCore.QRect(offset + 290, 0, 30, 20))
        self.wins.clicked.connect(partial(self.sort_mutations, self.wins))

        self.losses = SortingQLabel(self, True)
        self.losses.setText("L")
        self.losses.setAlignment(QtCore.Qt.AlignCenter)
        self.losses.setGeometry(QtCore.QRect(offset + 310, 0, 30, 20))
        self.losses.clicked.connect(partial(self.sort_mutations, self.losses))

        self.winrate = SortingQLabel(self, True)
        self.winrate.setText("Winrate")
        self.winrate.setGeometry(QtCore.QRect(offset + 340, 0, 60, 20))
        self.winrate.setAlignment(QtCore.Qt.AlignCenter)
        self.winrate.clicked.connect(partial(self.sort_mutations, self.winrate))

        self.difficulty = SortingQLabel(self, True)
        self.difficulty.setText("Completed")
        self.difficulty.setToolTip("The highest difficulty the mutation was completed on")
        self.difficulty.setAlignment(QtCore.Qt.AlignCenter)
        self.difficulty.setGeometry(QtCore.QRect(offset + 395, 0, 80, 20))
        self.difficulty.clicked.connect(partial(self.sort_mutations, self.difficulty))

        self.mutators = QtWidgets.QLabel("Mutators", self)
        self.mutators.setGeometry(QtCore.QRect(offset + 480, 0, 200, 20))

        self.line = Cline(self)
        self.line.setGeometry(QtCore.QRect(5, 22, 941, 1))

        for item in (self.name, self.map, self.wins, self.losses, self.winrate, self.difficulty, self.mutators):
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
        for mutation_name in weekly_mutations.keys():
            self.weekly_mutations[mutation_name] = MutationWidget(mutation_name)
            self.scroll_area_contentLayout.addWidget(self.weekly_mutations[mutation_name])

    def update_data(self, weekly_data):
        for mutation, widget in self.weekly_mutations.items():
            widget.update(weekly_data[mutation])
        self.sort_mutations(self)

    def sort_mutations(self, caller):
        if type(caller) is SortingQLabel:
            caller.activate()

        sort_by = SortingQLabel.active[self].value
        reverse = SortingQLabel.active[self].reverse
        widgets = list(self.weekly_mutations.values())

        # Remove widgets from layout
        for widget in widgets:
            self.scroll_area_contentLayout.removeWidget(widget)

        # Sort widgets
        trans = {"W": "wins", "L": "losses", "Winrate": "winrate", "Completed": "diff"}

        def sortingf(item: MutationWidget):
            # Data values (+ check if data saved for weekly widgets)
            if sort_by in trans and trans[sort_by] in item.data:
                return item.data[trans[sort_by]]
            # Mutation name
            elif sort_by == "Mutation":
                return item.mutation_name
            # Map
            return weekly_mutations[item.mutation_name]['map']

        widgets = sorted(widgets, key=sortingf, reverse=reverse)

        # Add widgets to the layout and update backgrounds
        for i, widget in enumerate(widgets):
            self.scroll_area_contentLayout.addWidget(widget)
            widget.bg.show() if i % 2 else widget.bg.hide()
