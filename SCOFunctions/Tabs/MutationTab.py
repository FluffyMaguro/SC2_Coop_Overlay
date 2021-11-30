from PyQt5 import QtWidgets, QtGui, QtCore
from SCOFunctions.SC2Dictionaries import weekly_mutations
from SCOFunctions.MUserInterface import Cline


class MutationWidget(QtWidgets.QWidget):
    def __init__(self, mutation_name: str, mutation_data):
        super().__init__()

        height = 22
        self.setGeometry(QtCore.QRect(0, 0, 931, 22))
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.name = QtWidgets.QLabel(mutation_name, self)
        self.name.setGeometry(QtCore.QRect(10, 0, 200, 20))

        self.map = QtWidgets.QLabel(mutation_data['map'], self)
        self.map.setGeometry(QtCore.QRect(200, 0, 200, 20))

        self.difficulty = QtWidgets.QLabel("None", self)
        self.difficulty.setGeometry(QtCore.QRect(350, 0, 100, 20))

        self.mutators = QtWidgets.QLabel('   |   '.join(mutation_data['mutators']), self)
        self.mutators.setGeometry(QtCore.QRect(420, 0, 600, 20))


class MutationTab(QtWidgets.QWidget):
    def __init__(self, parent, TabWidget):
        super().__init__()
        self.p = parent
        self.mutations = dict()

        # Labels
        offset = 10
        self.name = QtWidgets.QLabel("Mutation", self)
        self.name.setGeometry(QtCore.QRect(offset + 10, 0, 200, 20))

        self.map = QtWidgets.QLabel("Map", self)
        self.map.setGeometry(QtCore.QRect(offset + 200, 0, 200, 20))

        self.difficulty = QtWidgets.QLabel("Difficulty", self)
        self.difficulty.setToolTip("Maximum difficulty the mutation was completed on")
        self.difficulty.setGeometry(QtCore.QRect(offset + 350, 0, 100, 20))

        self.mutators = QtWidgets.QLabel("Mutators", self)
        self.mutators.setGeometry(QtCore.QRect(offset + 420, 0, 600, 20))

        self.line = Cline(self)
        self.line.setGeometry(QtCore.QRect(5, 22, 921, 1))

        # Scroll
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setGeometry(QtCore.QRect(0, 23, TabWidget.frameGeometry().width() - 5, TabWidget.frameGeometry().height() - 30))
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
        for mutation_name, mutation_data in weekly_mutations.items():
            self.mutations[mutation_name] = MutationWidget(mutation_name, mutation_data)
            self.scroll_area_contentLayout.addWidget(self.mutations[mutation_name])
