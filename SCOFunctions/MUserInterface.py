import os
import subprocess
import sys
import time
import traceback
from functools import partial

from PyQt5 import QtCore, QtGui, QtWebEngineWidgets, QtWidgets

import SCOFunctions.AppFunctions as AF
import SCOFunctions.HelperFunctions as HF
import SCOFunctions.MainFunctions as MF
from SCOFunctions.MainFunctions import show_overlay
from SCOFunctions.MFilePath import innerPath, truePath
from SCOFunctions.MLogging import Logger
from SCOFunctions.MTheming import MColors
from SCOFunctions.SC2Dictionaries import CommanderMastery, prestige_names
from SCOFunctions.Settings import Setting_manager as SM

if AF.isWindows():
    from PyQt5.QtWinExtras import QWinTaskbarButton

logger = Logger('UI', Logger.levels.INFO)
loggerJS = Logger('JS', Logger.levels.INFO)


def get_shadow():
    shadow = QtWidgets.QGraphicsDropShadowEffect()
    shadow.setBlurRadius(1)
    shadow.setOffset(2)
    shadow.setColor(QtGui.QColor(33, 33, 33))
    return shadow


def find_file(file):
    new_path = os.path.abspath(file)
    logger.info(f'Finding file {new_path}')
    if AF.isWindows():
        subprocess.Popen(f'explorer /select,"{new_path}"')
    else:
        subprocess.Popen(["open", new_path])


def fi(number):
    """ Formats integer to have spaces inbetween thousands"""
    if isinstance(number, int):
        return f'{number:,}'.replace(',', ' ')
    else:
        return str(number)


class Cline(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QtGui.QPalette.ButtonText)
        self.setEnabled(False)


class AmonUnitStats(QtWidgets.QWidget):
    """ Widget for amon's unit stats """
    def __init__(self, unit_data, parent=None):
        super().__init__(parent)
        self.setGeometry(QtCore.QRect(0, 0, 967, 433))

        # Scroll
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setGeometry(QtCore.QRect(0, 25, self.width(), self.height()))
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area_contents = QtWidgets.QWidget()
        self.scroll_area_contents.setGeometry(QtCore.QRect(0, 25, 961, 561))
        self.scroll_area_contents_layout = QtWidgets.QVBoxLayout()
        self.scroll_area_contents_layout.setAlignment(QtCore.Qt.AlignTop)
        self.scroll_area_contents_layout.setContentsMargins(10, 0, 0, 0)
        self.scroll_area_contents_layout.setSpacing(0)

        # Add heading
        self.heading = AmonUnitStatsUnit('Name', {
            'created': 'Created',
            'lost': 'Lost',
            'kills': 'Kills',
            'KD': 'K/D'
        },
                                         parent=self,
                                         sort=self.sort_units)
        self.heading.setGeometry(QtCore.QRect(10, 0, self.width(), 21))

        # Search
        self.search_label = QtWidgets.QLabel(self)
        self.search_label.setGeometry(QtCore.QRect(700, 35, 100, 21))
        self.search_label.setText('<b>Search for units</b>')

        self.ed_search = QtWidgets.QLineEdit(self)
        self.ed_search.setGeometry(QtCore.QRect(700, 55, 200, 20))
        self.ed_search.setAlignment(QtCore.Qt.AlignCenter)
        self.ed_search.setPlaceholderText("Search for units")
        self.ed_search.textChanged.connect(self.filter_units)

        # Add Amon's units
        self.update_data(unit_data, init=True)

        # Finalize
        self.scroll_area_contents.setLayout(self.scroll_area_contents_layout)
        self.scroll_area.setWidget(self.scroll_area_contents)
        self.show()

    def update_data(self, unit_data, init=False):
        """ Updates widget based on new unit data"""
        if not hasattr(self, 'units'):
            self.units = dict()

        # Contains widgets for units that are not present in currently generated data
        self.hidden_units = set()

        # Either create widgets or update current ones
        for idx, unit in enumerate(unit_data):
            if not unit in self.units:
                self.units[unit] = AmonUnitStatsUnit(unit, unit_data[unit], parent=self.scroll_area_contents, bg=idx % 2)
                self.scroll_area_contents_layout.addWidget(self.units[unit])
            else:
                self.units[unit].update_data(unit_data[unit])

        # Hide/show old widgets
        for unit in self.units:
            if not unit in unit_data:
                self.units[unit].hide()
                self.hidden_units.add(unit)

            elif unit in self.hidden_units:
                self.units[unit].show()
                self.hidden_units.remove(unit)

            else:
                self.units[unit].show()

        if init:
            self.update_backgrounds(init=True)
        else:
            self.sort_units()
            self.filter_units()

    def update_backgrounds(self, init=False):
        """ Updates background for all Amon's units"""
        idx = 0
        for i in range(self.scroll_area_contents_layout.count()):
            widget = self.scroll_area_contents_layout.itemAt(i).widget()
            if (init or widget.isVisible()) and not widget.search_name in {'sum', 'name'}:
                idx += 1
                widget.update_bg(idx % 2)

    def filter_units(self):
        """ Filters Amon's units based on text. Updates visibility and background."""
        text = self.ed_search.text().lower()
        for unit in self.units:
            if text in self.units[unit].search_name and not unit in self.hidden_units:
                self.units[unit].show()
            else:
                self.units[unit].hide()

        self.update_backgrounds()

    def sort_units(self, caller=None):
        """ Sorts Amon's units """
        trans_dict = {'Name': 'Name', 'Created': 'created', 'Lost': 'lost', 'Kills': 'kills', 'K/D': 'KD'}

        if type(caller) is SortingQLabel:
            caller.activate()

        sort_by = SortingQLabel.active[self].value
        reverse = SortingQLabel.active[self].reverse

        # Remove widgets from the layout
        for unit in self.units:
            self.scroll_area_contents_layout.removeWidget(self.units[unit])

        # Sort
        self.units = {k: v for k, v in sorted(self.units.items(), key=self.get_sortingf(trans_dict[sort_by]), reverse=reverse)}

        # Add widgets to the layout
        self.scroll_area_contents_layout.addWidget(self.units['sum'])
        for unit in self.units:
            if unit == 'sum':
                continue
            self.scroll_area_contents_layout.addWidget(self.units[unit])

        self.update_backgrounds()

    def get_sortingf(self, sortby):
        """ Returns None if sorting by name, otherwise custom sorting function """
        if sortby == 'Name':
            return None
        return partial(self.sortingf, sortby=sortby)

    @staticmethod
    def sortingf(data, sortby=None):
        unit = data[0]
        widget = data[1]

        if unit == 'sum':
            return 99999999999999
        if isinstance(widget.unit_data[sortby], str):
            return 9999999999999
        return widget.unit_data[sortby]


class AmonUnitStatsUnit(QtWidgets.QWidget):
    """ Widget for amon unit"""
    def __init__(self, unit, unit_data, parent=None, bg=False, sort=None):
        super().__init__(parent)
        self.p = parent
        height = 14 if unit != 'Name' else 26
        self.setGeometry(QtCore.QRect(0, 0, parent.width(), height))
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.search_name = unit.lower()

        self.bg = QtWidgets.QFrame(self)
        self.bg.setGeometry(QtCore.QRect(30, 1, 580, height))
        self.bg.setAutoFillBackground(True)
        self.bg.setBackgroundRole(QtGui.QPalette.AlternateBase)

        self.bg.hide()

        if unit in {'Name', 'sum'}:
            self.setStyleSheet("font-weight:bold")

        self.name = QtWidgets.QLabel(self) if unit != 'Name' else SortingQLabel(self)
        self.name.setGeometry(QtCore.QRect(40, 0, 160, height))
        self.name.setText(str(unit if unit != 'sum' else 'Total'))
        if unit == 'Name':
            self.name.setAlignment(QtCore.Qt.AlignVCenter)
            self.name.clicked.connect(partial(sort, self.name))
            self.line = Cline(self)
            self.line.setGeometry(QtCore.QRect(20, 24, 600, 1))

        self.elements = dict()
        for idx, item in enumerate(unit_data):
            self.elements[item] = QtWidgets.QLabel(self) if unit != 'Name' else SortingQLabel(self, True)
            self.elements[item].setGeometry(QtCore.QRect(100 + 100 * (idx + 1), 0, 100, height))

            if unit == 'Name':
                self.elements[item].clicked.connect(partial(sort, self.elements[item]))

            if item == 'KD':
                self.elements[item].setToolTip("Kill-death ratio")
                self.elements[item].setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
            else:
                self.elements[item].setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

        self.update_data(unit_data)
        if unit == 'Name':
            self.elements['created'].activate()
        self.show()

    def update_data(self, unit_data):
        """ Updates Amon's unit widget based on data provided"""
        self.unit_data = unit_data
        for idx, item in enumerate(unit_data):
            if item == 'KD':
                if isinstance(unit_data[item], str):
                    self.elements[item].setText(unit_data[item])
                else:
                    self.elements[item].setText(f"{unit_data[item]:.1f}")

            elif isinstance(unit_data[item], int):
                self.elements[item].setText(fi(unit_data[item]))
            else:
                self.elements[item].setText(str(unit_data[item]))

    def update_bg(self, bg):
        """ Changes whether the unit widget is to have background or not"""
        if bg:
            self.bg.show()
        else:
            self.bg.hide()


class UnitStats(QtWidgets.QWidget):
    """ Widget for unit stats """
    def __init__(self, unit_data, parent=None):
        super().__init__(parent)
        self.setGeometry(QtCore.QRect(0, 0, 950, 430))
        self.unit_data = unit_data
        self.which = 'main'

        self.heading_main = QtWidgets.QLabel(self)
        self.heading_main.setGeometry(QtCore.QRect(20, 2, 100, 20))
        self.heading_main.setText('<b>Main</b>')
        self.heading_main.setAlignment(QtCore.Qt.AlignCenter)

        self.heading_ally = QtWidgets.QLabel(self)
        self.heading_ally.setGeometry(QtCore.QRect(130, 2, 100, 20))
        self.heading_ally.setText('<b>Ally</b>')
        self.heading_ally.setAlignment(QtCore.Qt.AlignCenter)

        self.elements = dict()
        for idx, commander in enumerate(sorted(unit_data['main'].keys())):
            self.elements[('button', 'main', commander)] = QtWidgets.QPushButton(self)
            self.elements[('button', 'main', commander)].setGeometry(QtCore.QRect(20, idx * 22 + 20, 100, 25))
            self.elements[('button', 'main', commander)].setText(commander)
            self.elements[('button', 'main', commander)].clicked.connect(partial(self.update_units, commander=commander, main=True))

        for idx, commander in enumerate(sorted(unit_data['ally'].keys())):
            self.elements[('button', 'ally', commander)] = QtWidgets.QPushButton(self)
            self.elements[('button', 'ally', commander)].setGeometry(QtCore.QRect(130, idx * 22 + 20, 100, 25))
            self.elements[('button', 'ally', commander)].setText(commander)
            self.elements[('button', 'ally', commander)].clicked.connect(partial(self.update_units, commander=commander, main=False))

        self.WD_units = QtWidgets.QGroupBox(self)
        self.WD_units.p = self
        self.WD_units.setGeometry(QtCore.QRect(250, 10, self.width() - 250, self.height() - 20))
        self.WD_units.setTitle('Unit stats')

        self.left_offset = 10
        self.top_offset = 40

        self.heading = dict()
        for idx, item in enumerate(['Unit', 'Created', 'Freq', 'Lost', 'Lost%', 'Kills', 'K/D', 'Kills%']):
            self.heading[item] = SortingQLabel(self.WD_units, True if item != 'Unit' else False)
            self.heading[item].setGeometry(
                QtCore.QRect(self.left_offset + 20 if item == 'Unit' else self.left_offset + 120 + idx * 55, self.top_offset - 18, 60, 17))
            self.heading[item].setText(item)
            if item != 'Unit':
                self.heading[item].setAlignment(QtCore.Qt.AlignRight)
            if item == 'Kills%':
                self.heading[item].setToolTip(f"Typical percent of total kills")
            elif item == 'K/D':
                self.heading[item].setToolTip(f"Kill / death ratio")
            elif item == 'Lost%':
                self.heading[item].setToolTip('Units lost / created')
            elif item == 'Freq':
                self.heading[item].setToolTip('In what percent of games the unit was made')
            self.heading[item].hide()
            self.heading[item].setStyleSheet('font-weight: bold')

        self.note = QtWidgets.QLabel(self.WD_units)
        self.note.setGeometry(QtCore.QRect(self.WD_units.width() - 410, self.WD_units.height() - 20, 400, 20))
        self.note.setAlignment(QtCore.Qt.AlignRight)
        self.note.setText('* Kills from mind-controlled units are counted towards casters')
        self.note.setEnabled(False)

        self.show()

        self.heading['Unit'].activate()

        for idx, item in enumerate(['Unit', 'Created', 'Freq', 'Lost', 'Lost%', 'Kills', 'K/D', 'Kills%']):
            self.heading[item].clicked.connect(partial(self.update_units, caller=self.heading[item]))

    @staticmethod
    def sortingf(x, sortby=None):
        """ Sorting function for units"""
        if x[0] in ('sum', 'count'):
            return -1
        elif isinstance(x[1][sortby], int) or isinstance(x[1][sortby], float):
            return x[1][sortby]
        return 0

    def update_units(self, commander=None, main=None, caller=None):
        """ Updates unit stats for given commander and main/ally"""

        # Init variables. None values are coming from sort and will use self.attributes. Filled values come from buttons.
        if main is None:
            which = self.which
        else:
            which = 'main' if main else 'ally'
            self.which = which

        if commander is None and not hasattr(self, 'commander'):
            return  # Don't update if user hasn't clicked anything yet (updating after a new game)
        elif commander is None:
            commander = self.commander
        else:
            self.commander = commander

        # Update title
        self.WD_units.setTitle(f'Unit stats ({which.title()}) – {commander}')

        # Clean old elements
        if hasattr(self, 'units') and len(self.units) > 0:
            for u in self.units:
                self.units[u].deleteLater()

        self.units = dict()

        # Return if no data
        if not commander in self.unit_data[which]:
            return

        # Show heading
        for item in self.heading:
            self.heading[item].show()

        # Sort
        trans_dict = {
            'Unit': 'Name',
            'Created': 'created',
            'Lost': 'lost',
            'Lost%': 'lost_percent',
            'Kills': 'kills',
            'K/D': 'KD',
            'Kills%': 'kill_percentage',
            'Freq': 'made'
        }

        if type(caller) is SortingQLabel:
            caller.activate()

        sort_by = SortingQLabel.active[self].value
        reverse = SortingQLabel.active[self].reverse

        if sort_by == 'Unit':
            self.unit_data[which][commander] = {k: v for k, v in sorted(self.unit_data[which][commander].items(), reverse=reverse)}
        else:
            self.unit_data[which][commander] = {
                k: v
                for k, v in sorted(self.unit_data[which][commander].items(), key=partial(self.sortingf, sortby=trans_dict[sort_by]), reverse=reverse)
            }

        # Create lines for UnitStats
        idx = -1
        for unit in self.unit_data[which][commander]:
            # Don't workers and other unlikely units to get kills, their created/lost numbers would be very off
            if unit in {'count', 'Primal Hive', 'Primal Warden', 'Archangel'}:
                continue

            # Not sure what happened here, but Disruptors were created for Karax. Brood Queen is from gift mutator.
            if (commander == 'Karax' and unit == 'Disruptor') or (commander != 'Stukov' and unit == 'Brood Queen') or (commander != 'Tychus'
                                                                                                                       and unit == 'Auto-Turret'):
                continue

            # Don't show mind controlled units
            if self.unit_data[which][commander][unit]['created'] == 0 or (commander in {'Tychus', 'Vorazun', 'Zeratul', 'Abathur'}
                                                                          and unit in {'Broodling', 'Infested Terran'}):
                continue

            idx += 1
            if not idx % 2:
                self.units[('bg', unit)] = QtWidgets.QFrame(self.WD_units)
                self.units[('bg', unit)].setGeometry(QtCore.QRect(self.left_offset + 15, self.top_offset - 1 + idx * 17, 550, 17))
                self.units[('bg', unit)].setAutoFillBackground(True)
                self.units[('bg', unit)].setBackgroundRole(QtGui.QPalette.AlternateBase)

            self.units[('name', unit)] = QtWidgets.QLabel(self.WD_units)
            self.units[('name', unit)].setGeometry(QtCore.QRect(self.left_offset + 20, self.top_offset + idx * 17, 150, 17))
            name = unit if unit != 'sum' else f'Σ ({self.unit_data[which][commander]["count"]} games)'
            self.units[('name', unit)].setText(str(name))

            self.units[('created', unit)] = QtWidgets.QLabel(self.WD_units)
            self.units[('created', unit)].setGeometry(QtCore.QRect(self.left_offset + 175, self.top_offset + idx * 17, 60, 17))
            self.units[('created', unit)].setText(fi(self.unit_data[which][commander][unit]['created']))

            self.units[('made', unit)] = QtWidgets.QLabel(self.WD_units)
            self.units[('made', unit)].setGeometry(QtCore.QRect(self.left_offset + 230, self.top_offset + idx * 17, 60, 17))
            if self.unit_data[which][commander][unit]['made'] * 100 > 0:
                self.units[('made', unit)].setText(f"{self.unit_data[which][commander][unit]['made']*100:.0f}%")
            else:
                self.units[('made', unit)].setText("-")

            self.units[('lost', unit)] = QtWidgets.QLabel(self.WD_units)
            self.units[('lost', unit)].setGeometry(QtCore.QRect(self.left_offset + 285, self.top_offset + idx * 17, 60, 17))
            self.units[('lost', unit)].setText(fi(self.unit_data[which][commander][unit]['lost']))

            self.units[('lost_percent', unit)] = QtWidgets.QLabel(self.WD_units)
            self.units[('lost_percent', unit)].setGeometry(QtCore.QRect(self.left_offset + 340, self.top_offset + idx * 17, 60, 17))

            if self.unit_data[which][commander][unit]['lost_percent'] is not None:
                lost_percent = f"{100*self.unit_data[which][commander][unit]['lost_percent']:.0f}%"
            else:
                lost_percent = '-'
            self.units[('lost_percent', unit)].setText(lost_percent)
            self.units[('lost_percent', unit)].setToolTip('Units lost / created')

            self.units[('kills', unit)] = QtWidgets.QLabel(self.WD_units)
            self.units[('kills', unit)].setGeometry(QtCore.QRect(self.left_offset + 395, self.top_offset + idx * 17, 60, 17))
            self.units[('kills', unit)].setText(fi(self.unit_data[which][commander][unit]['kills']))

            self.units[('KD', unit)] = QtWidgets.QLabel(self.WD_units)
            self.units[('KD', unit)].setGeometry(QtCore.QRect(self.left_offset + 450, self.top_offset + idx * 17, 60, 17))
            self.units[('KD', unit)].setToolTip(f"Kill / death ratio")
            kd = self.unit_data[which][commander][unit]['KD']
            if kd is not None:
                self.units[('KD', unit)].setText(f"{kd:.1f}")
            else:
                self.units[('KD', unit)].setText("-")

            self.units[('percent', unit)] = QtWidgets.QLabel(self.WD_units)
            self.units[('percent', unit)].setGeometry(QtCore.QRect(self.left_offset + 505, self.top_offset + idx * 17, 60, 17))
            percent = self.unit_data[which][commander][unit]['kill_percentage']
            percent = percent if percent is not None else 0
            self.units[('percent', unit)].setText(f"{100*percent:.1f}%")
            self.units[('percent', unit)].setToolTip(f"Typical percent of total kills")

        for unit in self.units:
            if not unit[0] in {'name', 'bg'}:
                self.units[unit].setAlignment(QtCore.Qt.AlignRight)
            if unit[1] == 'sum':
                self.units[unit].setStyleSheet('font-weight: bold')
            self.units[unit].show()


class RegionStats(QtWidgets.QWidget):
    """Widget for region stats """
    def __init__(self, region, fdict, y, parent=None, bold=False, line=False, bg=False):
        super().__init__(parent)
        self.setGeometry(QtCore.QRect(15, y + 20, 700, 20))

        xspacing = 65
        width = 120

        if bg:
            self.bg = QtWidgets.QFrame(self)
            self.bg.setGeometry(QtCore.QRect(35, 2, self.width() - 30, 18))
            self.bg.setAutoFillBackground(True)
            self.bg.setBackgroundRole(QtGui.QPalette.AlternateBase)

        self.la_name = QtWidgets.QLabel(self)
        self.la_name.setGeometry(QtCore.QRect(0, 0, width, 20))
        self.la_name.setText(str(region))

        # Frequency
        self.la_frequency = QtWidgets.QLabel(self)
        self.la_frequency.setGeometry(QtCore.QRect(1 * xspacing + 2, 0, width, 20))
        if isinstance(fdict['frequency'], str):
            self.la_frequency.setText(fdict['frequency'])
        else:
            self.la_frequency.setText(f"{100*fdict['frequency']:.0f}%")

        # Wins
        self.la_wins = QtWidgets.QLabel(self)
        self.la_wins.setGeometry(QtCore.QRect(2 * xspacing, 0, width, 20))
        self.la_wins.setText(str(fdict['Victory']))

        # Losses
        self.la_losses = QtWidgets.QLabel(self)
        self.la_losses.setGeometry(QtCore.QRect(3 * xspacing, 0, width, 20))
        self.la_losses.setText(str(fdict['Defeat']))

        # Winrate
        self.la_winrate = QtWidgets.QLabel(self)
        self.la_winrate.setGeometry(QtCore.QRect(4 * xspacing, 0, width, 20))
        if isinstance(fdict['winrate'], str):
            self.la_winrate.setText(fdict['winrate'])
        else:
            self.la_winrate.setText(f"{100*fdict['winrate']:.0f}%")

        # Ascension level
        self.la_asc = QtWidgets.QLabel(self)
        self.la_asc.setGeometry(QtCore.QRect(5 * xspacing + 20, 0, width, 20))
        self.la_asc.setText(str(fdict['max_asc']))

        # Tried prestiges 4/18*3, tooltip
        self.la_prestiges = QtWidgets.QLabel(self)
        self.la_prestiges.setGeometry(QtCore.QRect(6 * xspacing + 60, 0, width, 20))
        if isinstance(fdict['prestiges'], str):
            self.la_prestiges.setText(fdict['prestiges'])
        else:
            total = 0
            text = ''
            for idx, co in enumerate(fdict['prestiges']):
                total += fdict['prestiges'][co]
                prest = fdict['prestiges'][co]
                if idx == len(fdict['prestiges']) - 1:
                    text += f"{co}: {prest}"
                else:
                    text += f"{co}: {prest}\n"

            self.la_prestiges.setText(f"{total}/54")
            self.la_prestiges.setToolTip(text)

        # Maxed commanders list
        self.la_commanders = QtWidgets.QLabel(self)
        self.la_commanders.setGeometry(QtCore.QRect(7 * xspacing + 95, 0, 160, 20))
        if isinstance(fdict['max_com'], str):
            self.la_commanders.setText(fdict['max_com'])
        else:
            if len(fdict['max_com']) < 4:
                self.la_commanders.setText(', '.join(fdict['max_com']))
            else:
                self.la_commanders.setText(f"{len(fdict['max_com'])}/18")

            self.la_commanders.setToolTip('\n'.join(fdict['max_com']))

        # Styling
        if bold:
            self.setStyleSheet('font-weight: bold')

        for item in {
                self.la_name, self.la_frequency, self.la_wins, self.la_losses, self.la_winrate, self.la_asc, self.la_prestiges, self.la_commanders
        }:
            item.setAlignment(QtCore.Qt.AlignCenter)

        if line:
            self.line = Cline(self)
            self.line.setGeometry(QtCore.QRect(34, 19, 660, 1))

        self.show()


class CommanderStats(QtWidgets.QWidget):
    """ Widget for detailed stats for allied commander (mastery, prestige)"""
    def __init__(self, commander, fanalysis, parent=None):
        super().__init__(parent)

        self.setGeometry(QtCore.QRect(485, 4, 500, 410))
        # Background
        self.fr_bg = QtWidgets.QLabel(self)
        self.fr_bg.setGeometry(QtCore.QRect(0, 0, 473, 87))
        self.fr_bg.setStyleSheet(f'background-color: black;')

        image_file = truePath(f'Layouts/Commanders/{commander}.png')
        if os.path.isfile(image_file):
            pixmap = QtGui.QPixmap(image_file)
            pixmap = pixmap.scaled(self.fr_bg.width(), self.fr_bg.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
            self.fr_bg.setPixmap(pixmap)

        # Commander name
        self.la_name = QtWidgets.QLabel(self)
        self.la_name.setGeometry(QtCore.QRect(0, 0, self.width() - 40, 87))
        self.la_name.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.la_name.setText(str(commander))
        self.la_name.setStyleSheet(f'font-weight: bold; font-size: 30px; color: white;')
        self.la_name.setGraphicsEffect(get_shadow())

        # Frequency
        self.la_frequency = QtWidgets.QLabel(self)
        self.la_frequency.setGeometry(QtCore.QRect(220, 98, 150, 25))
        self.la_frequency.setText(f"Frequency: <b>{100*fanalysis[commander]['Frequency']:.1f}%</b>")
        self.la_frequency.setAlignment(QtCore.Qt.AlignRight)

        # APM
        self.la_apm = QtWidgets.QLabel(self)
        self.la_apm.setGeometry(QtCore.QRect(290, 98, 180, 25))
        self.la_apm.setText(f"Median APM: <b>{fanalysis[commander]['MedianAPM']:.0f}</b>")
        self.la_apm.setAlignment(QtCore.Qt.AlignRight)

        # Mastery
        self.la_masteryH = QtWidgets.QLabel(self)
        self.la_masteryH.setGeometry(QtCore.QRect(5, 90, 300, 30))
        self.la_masteryH.setText('<h3><u>Mastery popularity</u></h3>')

        self.la_mastery = QtWidgets.QLabel(self)
        self.la_mastery.setGeometry(QtCore.QRect(5, 120, 300, 200))
        self.la_mastery.setAlignment(QtCore.Qt.AlignTop)
        text = ''
        for idx in fanalysis[commander]['Mastery']:
            if fanalysis[commander]['Mastery'][idx] == 1:
                fill = ''
            elif fanalysis[commander]['Mastery'][idx] >= 0.1:
                fill = '&nbsp;&nbsp;'
            else:
                fill = '&nbsp;&nbsp;&nbsp;&nbsp;'
            fill = fill if (idx % 2 == 1 or idx == 0) else '<br>' + fill
            text += f"{fill}<b>{100*fanalysis[commander]['Mastery'][idx]:.0f}%</b>&nbsp;&nbsp;{CommanderMastery[commander][idx]}<br>"

        self.la_mastery.setText(text)

        # Prestige
        self.la_prestigeH = QtWidgets.QLabel(self)
        self.la_prestigeH.setGeometry(QtCore.QRect(5, 240, 300, 30))
        self.la_prestigeH.setText('<h3><u>Prestige popularity</u></h3>')
        self.la_prestigeH.setToolTip('Prestige popularity is measured only after the patch introduced them')

        self.la_prestige = QtWidgets.QLabel(self)
        self.la_prestige.setGeometry(QtCore.QRect(5, 270, 300, 200))
        self.la_prestige.setAlignment(QtCore.Qt.AlignTop)
        self.la_prestige.setToolTip('Prestige popularity is measured only after the patch introduced them')

        text = ''
        for idx in fanalysis[commander]['Prestige']:
            if fanalysis[commander]['Prestige'][idx] == 1:
                fill = ''
            elif fanalysis[commander]['Prestige'][idx] >= 0.1:
                fill = '&nbsp;&nbsp;'
            else:
                fill = '&nbsp;&nbsp;&nbsp;&nbsp;'

            text += f"{fill}<b>{100*fanalysis[commander]['Prestige'][idx]:.0f}%</b>&nbsp;&nbsp;(P{idx})&nbsp;{prestige_names[commander][idx]}<br>"

        self.la_prestige.setText(text)

        self.show()


class FastestMap(QtWidgets.QWidget):
    """Custom widget for the fastest map"""
    def __init__(self, parent):
        super().__init__(parent)

        self.setGeometry(QtCore.QRect(485, 4, 485, 424))

        # Map frame
        self.fr_map = QtWidgets.QFrame(self)
        self.fr_map.setGeometry(QtCore.QRect(0, 2, 473, 87))

        # Map name
        self.la_name = QtWidgets.QLabel(self)
        self.la_name.setGeometry(QtCore.QRect(15, 20, 460, 40))
        self.la_name.setStyleSheet('font-weight: bold; font-size: 24px; color: white')
        self.la_name.setGraphicsEffect(get_shadow())

        # Time & enemy race
        self.la_time_race = QtWidgets.QLabel(self)
        self.la_time_race.setGeometry(QtCore.QRect(15, 48, 200, 20))
        self.la_time_race.setStyleSheet('color: white')

        # Player 1
        self.la_p1name = QtWidgets.QLabel(self)
        self.la_p1name.setGeometry(QtCore.QRect(10, 100, 225, 31))
        self.la_p1name.setStyleSheet('font-weight: bold')

        # P1 APM
        self.la_p1apm = QtWidgets.QLabel(self)
        self.la_p1apm.setGeometry(QtCore.QRect(10, 125, 100, 31))
        self.la_p1apm.setEnabled(False)

        # Player 2
        self.la_p2name = QtWidgets.QLabel(self)
        self.la_p2name.setGeometry(QtCore.QRect(245, 100, 201, 31))
        self.la_p2name.setStyleSheet('font-weight: bold')

        # P2 APM
        self.la_p2apm = QtWidgets.QLabel(self)
        self.la_p2apm.setGeometry(QtCore.QRect(245, 125, 100, 31))
        self.la_p2apm.setEnabled(False)

        # P1 Mastery
        self.la_p1masteries = QtWidgets.QLabel(self)
        self.la_p1masteries.setGeometry(QtCore.QRect(10, 165, 225, 91))

        # P2 Mastery
        self.la_p2masteries = QtWidgets.QLabel(self)
        self.la_p2masteries.setGeometry(QtCore.QRect(245, 165, 250, 91))

        # Find file button
        self.bt_findfile = QtWidgets.QPushButton(self)
        self.bt_findfile.setGeometry(QtCore.QRect(10, 369, 75, 23))
        self.bt_findfile.setText("Find file")

        # Show overlay button
        self.bt_showoverlay = QtWidgets.QPushButton(self)
        self.bt_showoverlay.setGeometry(QtCore.QRect(95, 369, 81, 23))
        self.bt_showoverlay.setText("Show overlay")

        # Date & difficulty
        self.la_date_difficulty = QtWidgets.QLabel(self)
        self.la_date_difficulty.setGeometry(QtCore.QRect(265, 379, 200, 20))
        self.la_date_difficulty.setAlignment(QtCore.Qt.AlignRight)
        self.la_date_difficulty.setEnabled(False)

        for item in {
                self.la_name, self.la_time_race, self.la_p1name, self.la_p1apm, self.la_p1masteries, self.la_p2name, self.la_p2apm,
                self.la_p2masteries, self.la_date_difficulty
        }:
            item.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

    def update_data(self, mapname, fdict, handles):
        """ Updates data based on replay dict from S2Parser"""

        image_path = innerPath(f"src/{mapname}.jpg")
        if os.path.isfile(image_path):
            image_path = image_path.replace('\\', '/')
            self.fr_map.setStyleSheet(f'background-image: url("{image_path}")')
        else:
            self.fr_map.setStyleSheet(f'background-image: none')

        self.la_name.setText(mapname)

        if fdict['length'] < 3600:
            length = time.strftime('%M:%S', time.gmtime(fdict['length']))
        else:
            length = time.strftime('%H:%M:%S', time.gmtime(fdict['length']))
        self.la_time_race.setText(f"{length} | {fdict.get('enemy_race','')}")

        if fdict['players'][0]['handle'] in handles:
            p1, p2 = 0, 1
        else:
            p1, p2 = 1, 0

        prestige = prestige_names[fdict['players'][p1]['commander']][fdict['players'][p1]['prestige']]
        self.la_p1name.setText(
            f"<h3>{fdict['players'][p1]['name']} ({fdict['players'][p1]['commander']})<br>{prestige} (P{fdict['players'][p1]['prestige']})</h3>")
        self.la_p1apm.setText(f"{fdict['players'][p1]['apm']} APM")
        self.la_p1masteries.setText(self.format_mastery(fdict['players'][p1]['commander'], fdict['players'][p1]['masteries']))

        prestige = prestige_names[fdict['players'][p2]['commander']][fdict['players'][p2]['prestige']]
        self.la_p2name.setText(
            f"<h3>{fdict['players'][p2]['name']} ({fdict['players'][p2]['commander']})<br>{prestige} (P{fdict['players'][p2]['prestige']})</h3>")
        self.la_p2apm.setText(f"{fdict['players'][p2]['apm']} APM")
        self.la_p2masteries.setText(self.format_mastery(fdict['players'][p2]['commander'], fdict['players'][p2]['masteries']))

        try:
            self.bt_findfile.clicked.disconnect()
            self.bt_showoverlay.clicked.disconnect()
        except Exception:
            pass

        self.bt_findfile.clicked.connect(lambda: find_file(fdict['file']))
        self.bt_showoverlay.clicked.connect(lambda: show_overlay(fdict['file']))

        self.la_date_difficulty.setText(f"{fdict['difficulty']} | {fdict['date'].replace(':','-',2).replace(':',' ',1)}")
        self.show()

    @staticmethod
    def format_mastery(commander: str, masterylist: list):
        text = ''
        for idx, mastery in enumerate(masterylist):
            fill = '' if mastery > 9 else '  '
            style = ' style="color:#aaa"' if mastery == 0 else ''
            text += f"<span{style}>{fill}{mastery}  {CommanderMastery[commander][idx]}</span><br>"
        return text


class CommanderEntry(QtWidgets.QWidget):
    """Custom widget for ally commander entry in stats"""
    def __init__(self, commander, frequency, wins, losses, winrate, apm, percent, y, button=True, bold=False, bg=False, parent=None, sort=None):
        super().__init__(parent)
        self.p = parent
        self.setGeometry(QtCore.QRect(15, y, 450, 25))

        # Button/label
        if button:
            self.bt_button = QtWidgets.QPushButton(self)
            self.bt_button.setGeometry(QtCore.QRect(0, 0, 150, 25))
        else:
            self.bt_button = SortingQLabel(self)
            self.bt_button.setGeometry(QtCore.QRect(0, 0, 150, 20))
            self.bt_button.setAlignment(QtCore.Qt.AlignCenter)
        self.bt_button.setText(commander)

        # Frequency
        self.la_frequency = QtWidgets.QLabel(self) if button else SortingQLabel(self, True)
        self.la_frequency.setGeometry(QtCore.QRect(150, 0, 60, 20))
        self.la_frequency.setAlignment(QtCore.Qt.AlignCenter)
        self.la_frequency.setToolTip('Commander frequency (corrected for your commander choices)')
        self.la_frequency.setText(str(frequency))

        # Wins
        self.la_wins = QtWidgets.QLabel(self) if button else SortingQLabel(self, True)
        self.la_wins.setGeometry(QtCore.QRect(200, 0, 50, 20))
        self.la_wins.setAlignment(QtCore.Qt.AlignCenter)
        self.la_wins.setText(str(wins))

        # Losses
        self.la_losses = QtWidgets.QLabel(self) if button else SortingQLabel(self, True)
        self.la_losses.setGeometry(QtCore.QRect(240, 0, 60, 20))
        self.la_losses.setAlignment(QtCore.Qt.AlignCenter)
        self.la_losses.setText(str(losses))

        # Winrate
        self.la_winrate = QtWidgets.QLabel(self) if button else SortingQLabel(self, True)
        self.la_winrate.setGeometry(QtCore.QRect(300, 0, 55, 20))
        self.la_winrate.setAlignment(QtCore.Qt.AlignCenter)
        self.la_winrate.setText(str(winrate))

        # Apm
        self.la_apm = QtWidgets.QLabel(self) if button else SortingQLabel(self, True)
        self.la_apm.setGeometry(QtCore.QRect(352, 0, 50, 20))
        self.la_apm.setAlignment(QtCore.Qt.AlignCenter)
        self.la_apm.setToolTip('Median APM')
        self.la_apm.setText(str(apm))

        # Kill percent
        self.la_killpercent = QtWidgets.QLabel(self) if button else SortingQLabel(self, True)
        self.la_killpercent.setGeometry(QtCore.QRect(395, 0, 60, 20))
        self.la_killpercent.setAlignment(QtCore.Qt.AlignCenter)
        percent = str(percent) if percent != '0%' else '–'
        self.la_killpercent.setText(percent)

        if percent == '–':
            self.la_killpercent.setToolTip('Typical percent of total kills<br><br>Run full analysis for this statistic.')
        else:
            self.la_killpercent.setToolTip('Typical percent of total kills')

        style = ''
        if bold:
            style += 'font-weight: bold;'
            self.bt_button.setStyleSheet('font-weight: bold')

        for item in {self.la_frequency, self.la_wins, self.la_losses, self.la_winrate, self.la_apm, self.la_killpercent}:
            item.setStyleSheet(style)
            if bg:
                item.setAutoFillBackground(True)
                item.setBackgroundRole(QtGui.QPalette.AlternateBase)

        # Activate sort and set events (only for header)
        if sort is not None:
            self.bt_button.activate()
            self.bt_button.clicked.connect(partial(sort, self.bt_button))
            self.la_frequency.clicked.connect(partial(sort, self.la_frequency))
            self.la_wins.clicked.connect(partial(sort, self.la_wins))
            self.la_losses.clicked.connect(partial(sort, self.la_losses))
            self.la_winrate.clicked.connect(partial(sort, self.la_winrate))
            self.la_apm.clicked.connect(partial(sort, self.la_apm))
            self.la_killpercent.clicked.connect(partial(sort, self.la_killpercent))

        self.show()


class MapEntry(QtWidgets.QWidget):
    """Custom widget for map entry in stats"""
    def __init__(self, parent, y, name, time_fastest, time_average, wins, losses, frequency, bonus, button=True, bold=False, bg=False, sort=None):
        super().__init__(parent)
        self.p = parent
        self.setGeometry(QtCore.QRect(7, y - 6, parent.width(), 40))
        if bold:
            self.setStyleSheet('font-weight: bold')

        # Button/label
        self.bt_button = QtWidgets.QPushButton(self) if button else SortingQLabel(self)
        self.bt_button.setGeometry(QtCore.QRect(0, 0, 135, 25))
        if not button:
            self.bt_button.setAlignment(QtCore.Qt.AlignCenter)
            self.bt_button.setGeometry(QtCore.QRect(0, 0, 135, 20))

        if 'Lock' in name and 'Load' in name:
            name = "Lock and Load"
        self.bt_button.setText(name)

        # Average time
        self.la_average = QtWidgets.QLabel(self) if not bold else SortingQLabel(self)
        self.la_average.setAlignment(QtCore.Qt.AlignCenter)
        self.la_average.setToolTip('Average victory time')
        time_average = time_average if time_average != 999999 else '–'
        if isinstance(time_average, int) or isinstance(time_average, float):
            self.la_average.setGeometry(QtCore.QRect(135, 0, 56, 24))
            if time_average < 3600:
                self.la_average.setText(time.strftime('%M:%S', time.gmtime(time_average)))
            else:
                self.la_average.setText(time.strftime('%H:%M:%S', time.gmtime(time_average)))

        elif time_average == '–':
            self.la_average.setGeometry(QtCore.QRect(135, 0, 56, 24))
        else:
            self.la_average.setGeometry(QtCore.QRect(132, 0, 60, 24))
            self.la_average.setText(time_average)

        # Fastest time
        self.la_fastest = QtWidgets.QLabel(self) if not bold else SortingQLabel(self)
        self.la_fastest.setGeometry(QtCore.QRect(178, 0, 70, 24))
        self.la_fastest.setAlignment(QtCore.Qt.AlignCenter)
        self.la_fastest.setToolTip('Fastest victory time')
        time_fastest = time_fastest if time_fastest != 999999 else '–'
        if isinstance(time_fastest, int) or isinstance(time_fastest, float):
            if time_fastest < 3600:
                self.la_fastest.setText(time.strftime('%M:%S', time.gmtime(time_fastest)))
            else:
                self.la_fastest.setText(time.strftime('%H:%M:%S', time.gmtime(time_fastest)))
        else:
            self.la_fastest.setText(time_fastest)

        # Frequency
        self.la_frequency = QtWidgets.QLabel(self) if not bold else SortingQLabel(self, True)
        self.la_frequency.setGeometry(QtCore.QRect(235, 0, 50, 24))
        self.la_frequency.setAlignment(QtCore.Qt.AlignCenter)
        if isinstance(frequency, str):
            self.la_frequency.setText(frequency)
        else:
            self.la_frequency.setText(f'{100*frequency:.1f}%')

        # Wins
        self.la_wins = QtWidgets.QLabel(self) if not bold else SortingQLabel(self, True)
        self.la_wins.setGeometry(QtCore.QRect(275, 0, 50, 24))
        self.la_wins.setAlignment(QtCore.Qt.AlignCenter)
        self.la_wins.setText(str(wins))

        # Losses
        self.la_losses = QtWidgets.QLabel(self) if not bold else SortingQLabel(self, True)
        self.la_losses.setGeometry(QtCore.QRect(316, 0, 54, 24))
        self.la_losses.setAlignment(QtCore.Qt.AlignCenter)
        self.la_losses.setText(str(losses))

        # Winrate
        self.la_winrate = QtWidgets.QLabel(self) if not bold else SortingQLabel(self, True)
        self.la_winrate.setGeometry(QtCore.QRect(367, 0, 50, 24))
        self.la_winrate.setAlignment(QtCore.Qt.AlignCenter)
        if isinstance(wins, str) or isinstance(losses, str):
            winrate = 'Win%'
        else:
            winrate = '-'
            if wins or losses > 0:
                winrate = f"{100*wins/(wins+losses):.0f}%"
        self.la_winrate.setText(winrate)

        # Bonus
        self.la_bonus = QtWidgets.QLabel(self) if not bold else SortingQLabel(self, True)
        self.la_bonus.setGeometry(QtCore.QRect(412, 0, 50, 24))
        self.la_bonus.setAlignment(QtCore.Qt.AlignCenter)
        if bonus == 0:
            self.la_bonus.setText('–')
            self.la_bonus.setToolTip(
                'Bonus objective completion. Completing half of bonus objectives counts as 50%.<br><br>Run full analysis for this statistic.')
        elif isinstance(bonus, int) or isinstance(bonus, float):
            self.la_bonus.setText(f'{100*bonus:.0f}%')
            self.la_bonus.setToolTip('Bonus objective completion. Completing half of bonus objectives counts as 50%.')
        else:
            self.la_bonus.setText(str(bonus))
            self.la_bonus.setToolTip('Bonus objective completion. Completing half of bonus objectives counts as 50%.')

        # Activate sort and set events (only for header)
        if sort is not None:
            self.bt_button.activate()
            self.bt_button.clicked.connect(partial(sort, self.bt_button))
            self.la_average.clicked.connect(partial(sort, self.la_average))
            self.la_fastest.clicked.connect(partial(sort, self.la_fastest))
            self.la_frequency.clicked.connect(partial(sort, self.la_frequency))
            self.la_wins.clicked.connect(partial(sort, self.la_wins))
            self.la_losses.clicked.connect(partial(sort, self.la_losses))
            self.la_winrate.clicked.connect(partial(sort, self.la_winrate))
            self.la_bonus.clicked.connect(partial(sort, self.la_bonus))

        self.show()

        if bg:
            for item in {self.la_average, self.la_fastest, self.la_frequency, self.la_wins, self.la_losses, self.la_winrate, self.la_bonus}:
                item.setAutoFillBackground(True)
                item.setBackgroundRole(QtGui.QPalette.AlternateBase)


class DifficultyEntry(QtWidgets.QWidget):
    """Custom widget for difficulty entry in stats"""
    def __init__(self, name, wins, losses, winrate, x, y, bold=False, line=False, bg=False, parent=None):
        super().__init__(parent)

        self.setGeometry(QtCore.QRect(x, y + 150, 300, 40))

        if bg:
            self.bg = QtWidgets.QFrame(self)
            self.bg.setGeometry(QtCore.QRect(0, 13, 225, 16))
            self.bg.setAutoFillBackground(True)
            self.bg.setBackgroundRole(QtGui.QPalette.AlternateBase)

        self.la_name = QtWidgets.QLabel(self)
        self.la_name.setGeometry(QtCore.QRect(10, 10, 70, 20))
        self.la_name.setText(str(name))

        self.la_wins = QtWidgets.QLabel(self)
        self.la_wins.setGeometry(QtCore.QRect(60, 10, 70, 20))
        self.la_wins.setAlignment(QtCore.Qt.AlignCenter)
        self.la_wins.setText(str(wins))

        self.la_losses = QtWidgets.QLabel(self)
        self.la_losses.setGeometry(QtCore.QRect(110, 10, 70, 20))
        self.la_losses.setAlignment(QtCore.Qt.AlignCenter)
        self.la_losses.setText(str(losses))

        self.la_winrate = QtWidgets.QLabel(self)
        self.la_winrate.setGeometry(QtCore.QRect(180, 10, 50, 20))
        self.la_winrate.setAlignment(QtCore.Qt.AlignCenter)
        self.la_winrate.setText(str(winrate))

        if bold:
            self.setStyleSheet('font-weight: bold;')

        if line:
            self.line = Cline(self)
            self.line.setGeometry(QtCore.QRect(0, 30, 235, 1))

        self.show()


class GameEntry:
    """ 
    Class for UI elements in games tab. 
    It takes `replay_dict` generated by s2parser. 
    """
    def __init__(self, replay_dict, handles, parent):
        self.mapname = replay_dict.map_name
        self.result = replay_dict.result
        self.difficulty = replay_dict.ext_difficulty
        self.enemy = replay_dict.enemy_race
        self.length = replay_dict.form_alength
        self.file = replay_dict.file
        self.date = replay_dict.date[:10].replace(':', '-') + ' ' + replay_dict.date[11:16]
        self.chat_showing = False
        self.message_count = len(replay_dict.messages)

        if replay_dict.players[1]['handle'] in handles:
            self.p1_name = replay_dict.players[1]['name']
            self.p1_commander = replay_dict.players[1]['commander']
            self.p1_handle = replay_dict.players[1]['handle']
            self.p2_name = replay_dict.players[2].get('name', '')
            self.p2_commander = replay_dict.players[2].get('commander')
            self.p2_handle = replay_dict.players[2].get('handle', '')
        else:
            self.p1_name = replay_dict.players[2].get('name')
            self.p1_commander = replay_dict.players[2].get('commander')
            self.p1_handle = replay_dict.players[2].get('handle')
            self.p2_name = replay_dict.players[1]['name']
            self.p2_commander = replay_dict.players[1]['commander']
            self.p2_handle = replay_dict.players[1]['handle']

        height = 30
        line_spacing = 7

        self.widget = QtWidgets.QWidget(parent)
        self.widget.setGeometry(QtCore.QRect(0, 0, 931, height))
        self.widget.setMinimumHeight(height)
        self.widget.setMaximumHeight(height)

        self.line = Cline(self.widget)
        self.line.setGeometry(QtCore.QRect(10, 0, 921, 1))

        self.la_mapname = QtWidgets.QLabel(self.widget)
        self.la_mapname.setGeometry(QtCore.QRect(20, line_spacing, 125, 21))
        self.la_mapname.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.la_mapname.setText(self.mapname)

        self.la_result = QtWidgets.QLabel(self.widget)
        self.la_result.setGeometry(QtCore.QRect(135, line_spacing, 50, 21))
        self.la_result.setAlignment(QtCore.Qt.AlignCenter)
        self.la_result.setText(self.result)

        self.la_p1 = QtWidgets.QLabel(self.widget)
        self.la_p1.setGeometry(QtCore.QRect(160, line_spacing, 200, 21))
        self.la_p1.setAlignment(QtCore.Qt.AlignCenter)
        self.la_p1.setText(f'{self.p1_name} ({self.p1_commander})')
        self.la_p1.setToolTip(f"Unique handle: {self.p1_handle}")

        self.la_p2 = QtWidgets.QLabel(self.widget)
        self.la_p2.setGeometry(QtCore.QRect(295, line_spacing, 200, 21))
        self.la_p2.setAlignment(QtCore.Qt.AlignCenter)
        self.la_p2.setText(f'{self.p2_name} ({self.p2_commander})')
        self.la_p2.setToolTip(f"Unique handle: {self.p2_handle}")

        self.la_enemy = QtWidgets.QLabel(self.widget)
        self.la_enemy.setGeometry(QtCore.QRect(475, line_spacing, 41, 20))
        self.la_enemy.setAlignment(QtCore.Qt.AlignCenter)
        self.la_enemy.setText(self.enemy)

        self.la_length = QtWidgets.QLabel(self.widget)
        self.la_length.setGeometry(QtCore.QRect(515, line_spacing, 71, 20))
        self.la_length.setAlignment(QtCore.Qt.AlignCenter)
        self.la_length.setText(self.length)

        self.la_difficulty = QtWidgets.QLabel(self.widget)
        self.la_difficulty.setGeometry(QtCore.QRect(570, line_spacing, 81, 20))
        self.la_difficulty.setAlignment(QtCore.Qt.AlignCenter)
        self.la_difficulty.setText(self.difficulty)

        self.la_date = QtWidgets.QLabel(self.widget)
        self.la_date.setGeometry(QtCore.QRect(645, line_spacing, 101, 20))
        self.la_date.setAlignment(QtCore.Qt.AlignCenter)
        self.la_date.setText(self.date)

        self.BT_show = QtWidgets.QPushButton(self.widget)
        self.BT_show.setGeometry(QtCore.QRect(750, line_spacing, 55, 23))
        self.BT_show.setText("Overlay")
        self.BT_show.clicked.connect(lambda: show_overlay(self.file))

        self.BT_chat = QtWidgets.QPushButton(self.widget)
        self.BT_chat.setGeometry(QtCore.QRect(810, line_spacing, 55, 23))
        self.BT_chat.setText("Chat")
        self.BT_chat.clicked.connect(self.show_chat)

        self.BT_file = QtWidgets.QPushButton(self.widget)
        self.BT_file.setGeometry(QtCore.QRect(870, line_spacing, 55, 23))
        self.BT_file.setText("File")
        self.BT_file.clicked.connect(lambda: find_file(self.file))

        self.la_chat = QtWidgets.QLabel(self.widget)
        self.la_chat.setGeometry(QtCore.QRect(20, 35, 500, 10 + 14 * self.message_count))
        self.la_chat.setAlignment(QtCore.Qt.AlignTop)

        testplayer = 2 if replay_dict.players[1]['handle'] in handles else 1

        text = ''
        for message in replay_dict.messages:
            color = MColors.chat_other if message['player'] == testplayer else MColors.chat_main

            if message['time'] >= 3600:
                t = time.strftime('%H:%M:%S', time.gmtime(message['time']))
            else:
                t = time.strftime('%M:%S', time.gmtime(message['time']))
            style = f'style="color: {color}"'
            text += f"<span {style}>{t}&nbsp;&nbsp;<b>{replay_dict.players[message['player']].get('name','–')}</b>:&nbsp;&nbsp;{message['text']}</span><br>"

        self.la_chat.setText(text)
        self.la_chat.hide()

        # Styling
        for item in {
                self.la_chat, self.la_mapname, self.la_result, self.la_p1, self.la_p2, self.la_enemy, self.la_length, self.la_difficulty, self.la_date
        }:
            item.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            if self.result == 'Defeat':
                item.setStyleSheet(f'QLabel {{color: {MColors.game_defeat}}}')
            elif replay_dict.weekly:
                item.setStyleSheet(f'QLabel {{color: {MColors.game_weekly}}}')

    def show_chat(self):
        """ Shows/hides chat """
        if self.chat_showing:
            self.chat_showing = False
            height = 30
            self.la_chat.hide()
        else:
            self.chat_showing = True
            height = 30 + (10 + 14 * self.message_count) if self.message_count > 0 else 50
            self.la_chat.show()

        self.widget.setGeometry(QtCore.QRect(0, 0, self.widget.width(), height))
        self.widget.setMinimumHeight(height)
        self.widget.setMaximumHeight(height)


class PlayerEntry:
    """ 
    Class for UI elements in players tab. 

    """
    def __init__(self, player, winrate_data, note, parent):
        self.name = player
        self.note = note
        self.winrate_data = winrate_data

        self.height = 35
        line_spacing = 7

        self.widget = QtWidgets.QWidget(parent)
        self.widget.setGeometry(QtCore.QRect(0, 0, 931, self.height))
        self.widget.setMinimumHeight(self.height)
        self.widget.setMaximumHeight(self.height)

        self.line = Cline(self.widget)
        self.line.setGeometry(QtCore.QRect(10, 33, 921, 1))

        self.la_name = QtWidgets.QLabel(self.widget)
        self.la_name.setGeometry(QtCore.QRect(20, line_spacing, 150, 21))
        self.la_name.setText(self.name)

        self.la_wins = QtWidgets.QLabel(self.widget)
        self.la_wins.setGeometry(QtCore.QRect(150, line_spacing, 31, 21))
        self.la_wins.setAlignment(QtCore.Qt.AlignCenter)

        self.la_losses = QtWidgets.QLabel(self.widget)
        self.la_losses.setGeometry(QtCore.QRect(205, line_spacing, 41, 21))
        self.la_losses.setAlignment(QtCore.Qt.AlignCenter)

        self.la_winrate = QtWidgets.QLabel(self.widget)
        self.la_winrate.setGeometry(QtCore.QRect(260, line_spacing, 51, 21))
        self.la_winrate.setAlignment(QtCore.Qt.AlignCenter)

        self.la_apm = QtWidgets.QLabel(self.widget)
        self.la_apm.setGeometry(QtCore.QRect(315, line_spacing, 51, 21))
        self.la_apm.setAlignment(QtCore.Qt.AlignCenter)
        self.la_apm.setToolTip("Median APM")

        self.la_kills = QtWidgets.QLabel(self.widget)
        self.la_kills.setGeometry(QtCore.QRect(370, line_spacing, 51, 21))
        self.la_kills.setAlignment(QtCore.Qt.AlignCenter)
        self.la_kills.setToolTip("Median percent of kills")

        self.la_commander = QtWidgets.QLabel(self.widget)
        self.la_commander.setGeometry(QtCore.QRect(420, line_spacing, 81, 21))
        self.la_commander.setAlignment(QtCore.Qt.AlignCenter)
        self.la_commander.setToolTip("The most played commander")

        self.la_frequency = QtWidgets.QLabel(self.widget)
        self.la_frequency.setGeometry(QtCore.QRect(500, line_spacing, 51, 21))
        self.la_frequency.setAlignment(QtCore.Qt.AlignCenter)
        self.la_frequency.setToolTip("The most played commander frequency")

        self.ed_note = QtWidgets.QLineEdit(self.widget)
        self.ed_note.setGeometry(QtCore.QRect(580, line_spacing, 300, 21))
        self.ed_note.setAlignment(QtCore.Qt.AlignCenter)
        if not self.note in {None, ''}:
            self.ed_note.setText(self.note)

        self.handles_UI = dict()
        self.expanded = False

        # This is necessary only sometimes (when the user is looking at the tab while its updating )
        for item in {self.widget, self.line, self.la_name, self.la_wins, self.la_losses, self.la_winrate, self.ed_note, self.la_kills, self.la_apm}:
            item.mouseReleaseEvent = self.expand
            item.show()

        for item in {self.la_name, self.la_wins, self.la_losses, self.la_winrate, self.la_kills, self.la_apm}:
            item.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.update_winrates(winrate_data)

    def get_note(self):
        return self.ed_note.text()

    def show(self):
        self.widget.show()

    def hide(self):
        self.widget.hide()

    def highlight(self, b: bool):
        self.create_handles()
        for item in (self.line, self.la_name, self.la_wins, self.la_losses, self.la_winrate, self.ed_note, self.la_kills, self.la_apm,
                     self.la_commander, self.la_frequency):
            if b:
                item.setStyleSheet(f'QLabel {{color: {MColors.player_highlight}; font-weight: bold}}')
            else:
                item.setStyleSheet('QLabel {}')

        # Highlight the last handle
        max_date = max(self.winrate_data[handle][6] for handle in self.winrate_data if handle != "total")
        max_handle = [handle for handle in self.winrate_data if (handle != "total" and self.winrate_data[handle][6] == max_date)][0]
        for handle in self.handles_UI:
            for widget in self.handles_UI[handle]:
                if handle == max_handle and b:
                    self.handles_UI[handle][widget].setStyleSheet(f'QLabel {{color: {MColors.player_highlight}; font-weight: bold}}')
                else:
                    self.handles_UI[handle][widget].setStyleSheet('QLabel {}')

    def expand(self, *args):
        """ Expand/deexpand handle information"""
        if not self.expanded:
            self.expanded = True
            # Update size
            handles = tuple(handle for handle in self.winrate_data if handle != 'total')
            new_height = self.height - 10
            self.widget.setFixedHeight(10 + new_height * (1 + len(handles)))
            self.line.move(10, 33 + new_height * len(handles))

            # Create and update handle information
            self.create_handles()  # Also updates with new handles
            self.update_handles()
            for handle in self.handles_UI:
                for widget in self.handles_UI[handle]:
                    self.handles_UI[handle][widget].show()
        else:
            self.expanded = False
            # Back to the original size
            self.widget.setFixedHeight(self.height)
            self.line.move(10, 33)
            # Hide handle information
            for handle in self.handles_UI:
                for widget in self.handles_UI[handle]:
                    self.handles_UI[handle][widget].hide()

    def create_handles(self):
        """ Creates new handles"""
        new_height = self.height - 10

        for idx, handle in enumerate(self.winrate_data):
            if handle in self.handles_UI or handle == 'total':
                continue

            item_height = 10 + new_height * (1 + idx)
            name = QtWidgets.QLabel(self.widget)
            name.setGeometry(QtCore.QRect(20, item_height, 150, 21))

            wins = QtWidgets.QLabel(self.widget)
            wins.setGeometry(QtCore.QRect(150, item_height, 31, 21))
            wins.setAlignment(QtCore.Qt.AlignCenter)

            losses = QtWidgets.QLabel(self.widget)
            losses.setGeometry(QtCore.QRect(205, item_height, 41, 21))
            losses.setAlignment(QtCore.Qt.AlignCenter)

            winrate = QtWidgets.QLabel(self.widget)
            winrate.setGeometry(QtCore.QRect(260, item_height, 51, 21))
            winrate.setAlignment(QtCore.Qt.AlignCenter)

            apm = QtWidgets.QLabel(self.widget)
            apm.setGeometry(QtCore.QRect(315, item_height, 51, 21))
            apm.setAlignment(QtCore.Qt.AlignCenter)

            kills = QtWidgets.QLabel(self.widget)
            kills.setGeometry(QtCore.QRect(370, item_height, 51, 21))
            kills.setAlignment(QtCore.Qt.AlignCenter)

            commander = QtWidgets.QLabel(self.widget)
            commander.setGeometry(QtCore.QRect(420, item_height, 81, 21))
            commander.setAlignment(QtCore.Qt.AlignCenter)

            frequency = QtWidgets.QLabel(self.widget)
            frequency.setGeometry(QtCore.QRect(500, item_height, 51, 21))
            frequency.setAlignment(QtCore.Qt.AlignCenter)

            self.handles_UI[handle] = {
                "name": name,
                "wins": wins,
                "losses": losses,
                "winrate": winrate,
                "apm": apm,
                "kills": kills,
                "commander": commander,
                "frequency": frequency
            }

            for widget in self.handles_UI[handle].values():
                opacity_effect = QtWidgets.QGraphicsOpacityEffect()
                opacity_effect.setOpacity(0.6)
                widget.setGraphicsEffect(opacity_effect)
                widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

    def update_handles(self):
        """ Update handle information with new data"""
        if not len(self.handles_UI):
            return

        data = self.winrate_data
        for handle, widgets in self.handles_UI.items():
            widgets["name"].setText(f"{handle} ({HF.get_region(handle)})")
            widgets["name"].setToolTip(f"Last game played: {HF.get_time_difference(data[handle][6])}")
            widgets["wins"].setText(str(data[handle][0]))
            widgets["losses"].setText(str(data[handle][1]))
            win_loss = data[handle][0] / (data[handle][0] + data[handle][1])
            widgets["winrate"].setText(f"{win_loss:.0%}")
            widgets["apm"].setText(f"{data[handle][2]:.0f}")
            widgets["kills"].setText(f"{data[handle][5]:.0%}")
            widgets["commander"].setText(data[handle][3])
            widgets["frequency"].setText(f"{data[handle][4]:.0%}")

    def update_winrates(self, data):
        """ Updates winrate for the player. """
        self.winrate_data = data
        if self.expanded:
            self.create_handles()  # Also updates with new data
        self.update_handles()

        data = data['total']
        self.wins = data[0]
        self.losses = data[1]
        self.winrate = 100 * self.wins / (self.wins + self.losses)

        self.la_name.setToolTip(f"Last game played: {HF.get_time_difference(data[6])}")
        self.la_wins.setText(str(self.wins))
        self.la_losses.setText(str(self.losses))
        self.la_winrate.setText(f'{self.winrate:.0f}%')
        self.la_apm.setText(f'{data[2]:.0f}')
        self.la_kills.setText(f'{100*data[5]:.0f}%')
        self.la_commander.setText(str(data[3]))
        self.la_frequency.setText(f'{100*data[4]:.0f}%')


class WorkerSignals(QtCore.QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing, anything

    '''
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(object)


class Worker(QtCore.QRunnable):
    """
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    The function callback to run on this worker thread. Supplied args and kwargs will be passed through to the runner.
    `fn` function
    `arg` Arguments to pass to the callback function
    `kwargs` Keywords to pass to the callback function
    """
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        if 'progress_callback' in kwargs:
            self.kwargs['progress_callback'] = self.signals.progress

    @QtCore.pyqtSlot()
    def run(self):
        """ Runs the function and emits signals (error, result, finished) """
        try:
            try:
                result = self.fn(*self.args, **self.kwargs)
            except Exception:
                logger.error(traceback.format_exc())
                exctype, value = sys.exc_info()[:2]
                self.signals.error.emit((exctype, value, traceback.format_exc()))
            else:
                self.signals.result.emit(result)
            finally:
                self.signals.finished.emit()
        except RuntimeError:
            logger.debug('Error with pyqt thread. The app likely closed.')
        except Exception:
            logger.error(traceback.format_exc())


class CustomKeySequenceEdit(QtWidgets.QKeySequenceEdit):
    def __init__(self, parent=None):
        super(CustomKeySequenceEdit, self).__init__(parent)

    def keyPressEvent(self, QKeyEvent):
        super(CustomKeySequenceEdit, self).keyPressEvent(QKeyEvent)
        value = self.keySequence()
        self.setKeySequence(QtGui.QKeySequence(value))

    def get_hotkey_string(self) -> str:
        """ Returns the hotkey string usable by the keyboard module"""
        hotkey = self.keySequence().toString()
        replace_dict = {"Num+": "", "scrolllock": 'scroll lock', "ScrollLock": 'scroll lock'}
        for item, nitem in replace_dict.items():
            hotkey = hotkey.replace(item, nitem)
        return hotkey


class TitleBar(QtWidgets.QFrame):
    """ Custom title bar used in the dark theme. Handles minimization, closing and dragging the window."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setGeometry(QtCore.QRect(582, 0, 468, 24))
        self.moving = False
        self.offset = None
        self.parent = parent

        # New title
        self.new_title = QtWidgets.QLabel(self)
        self.new_title.setGeometry(QtCore.QRect(100, 1, 200, 20))
        self.new_title.setStyleSheet("color: white; font-weight: bold")

        # Minimize button
        self.minimize = QtWidgets.QToolButton(self)
        self.minimize.setGeometry(QtCore.QRect(355, 2, 20, 20))
        self.minimize.setText('–')
        self.minimize.clicked.connect(parent.showMinimized)

        # Maximize button
        self.close_button = QtWidgets.QToolButton(self)
        self.close_button.setGeometry(QtCore.QRect(375, 2, 20, 20))
        self.close_button.setText('⨉')
        self.close_button.clicked.connect(parent.minimize_to_tray)

    def mousePressEvent(self, event):
        if self.parent.dark_mode_active and event.button() == QtCore.Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.parent.dark_mode_active and self.moving:
            self.parent.move(event.globalPos() - self.offset - QtCore.QPoint(512, 0))


class CustomQTabWidget(QtWidgets.QTabWidget):
    """ Main app widget """
    def __init__(self, parent=None):
        super(CustomQTabWidget, self).__init__(parent)

        # Tray
        self.tray_icon = QtWidgets.QSystemTrayIcon()
        self.tray_icon.setIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        self.tray_icon.activated.connect(self.tray_activated)
        self.tray_menu = QtWidgets.QMenu()
        self.tray_menu.setStyleSheet("background-color: #272E3B; color: #fff")

        self.show_action = QtWidgets.QAction("   Show ")
        self.show_action.triggered.connect(self.show)
        self.show_action.setIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        self.tray_menu.addAction(self.show_action)

        self.tray_menu.addSeparator()

        self.quit_action = QtWidgets.QAction("   Quit ")
        self.quit_action.setIcon(self.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DialogCancelButton')))
        self.quit_action.triggered.connect(QtWidgets.qApp.quit)
        self.tray_menu.addAction(self.quit_action)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

        # For dark mode
        self.dark_mode_active = False
        self.title_bar = TitleBar(self)
        self.title_bar.hide()

        self.taskbar_progress = None

    def showEvent(self, evt):
        """ Create a progress bar on the taskbar for Windows"""
        if AF.isWindows() and not self.taskbar_progress is not None:
            self.taskbar_button = QWinTaskbarButton()
            self.taskbar_progress = self.taskbar_button.progress()
            self.taskbar_progress.setRange(0, 100)
            self.taskbar_progress.setValue(0)
            self.taskbar_button.setWindow(self.windowHandle())
            self.taskbar_progress.hide()

    @QtCore.pyqtSlot(bool)
    def closeEvent(self, event):
        """ Overriding close event and minimizing instead """
        # This is only necessary for white theme. Chaning this might improve the apps behavior when auto-closing
        if not SM.settings['dark_theme']:
            event.ignore()
            self.minimize_to_tray()

    def minimize_to_tray(self):
        if SM.settings['minimize_to_tray']:
            self.hide()
            self.show_minimize_message()
        else:
            QtWidgets.qApp.quit()

    def format_close_message(self):
        """ Shows few hotkeys in the notification area"""
        text = ''
        setting_dict = {"hotkey_show/hide": "Show/Hide", "hotkey_newer": "Newer replay", "hotkey_older": "Older replay"}
        for key in setting_dict:
            if key in SM.settings and SM.settings[key] != '':
                text += f"\n{SM.settings[key]} → {setting_dict[key]}"
        return text

    def show_minimize_message(self):
        self.tray_icon.showMessage("StarCraft Co-op Overlay", f"App was minimized into the tray{self.format_close_message()}",
                                   QtGui.QIcon(innerPath('src/OverlayIcon.ico')), 2000)

    def show_update_message(self):
        self.tray_icon.showMessage("StarCraft Co-op Overlay", f"New version available!", QtGui.QIcon(innerPath('src/OverlayIcon.ico')), 2000)

    def tray_activated(self, reason):
        """ Hides/shows main window when the tray icon is double clicked """
        if reason == 2:
            if self.isVisible():
                self.hide()
            else:
                #Change flags briefly to bring to front
                self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                self.show()
                if self.dark_mode_active:
                    self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
                else:
                    self.setWindowFlags(QtCore.Qt.Window)
                self.show()


class CustomWebView(QtWebEngineWidgets.QWebEngineView):
    """ Expanding this class to add javascript after page is loaded. This is could be used to distinquish main overlay from other overlays (e.g. in OBS)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loadFinished.connect(self.on_load_finished)

    @QtCore.pyqtSlot(bool)
    def on_load_finished(self, ok):
        if ok:
            self.page().runJavaScript(f"do_not_use_websocket = true;")
            MF.resend_init_message()


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    """ Custom webengine page for logging javascript messages"""
    def __init__(self, parent=None):
        super().__init__(parent)

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        loggerJS.info(f"{msg} | line: {line} ({sourceID})")


class PatchNotes(QtWidgets.QWidget):
    """ Widget for showing patchnotes """
    def __init__(self, version, parent=None, icon=None, patchnotes=None):
        super().__init__(parent)

        release = f"{str(version)[0]}.{str(version)[1:]}"
        height = 50 + len(patchnotes) * 18
        width = 490
        text = ''

        # Add text, calculate required width
        for line in patchnotes:
            text += f'&middot; {line}<br>'
            width = width if width > len(line) * 6 + 40 else len(line) * 6 + 40

        font = self.font()
        font.setPointSize(font.pointSize() * 1.2)

        self.setWindowTitle(f'New release changelog')
        self.setWindowIcon(icon)
        self.setFixedSize(width, height)

        self.la_heading = QtWidgets.QLabel(self)
        self.la_heading.setGeometry(QtCore.QRect(0, 10, self.width(), 30))
        self.la_heading.setText(f'<h1>StarCraft Co-op Overlay ({release})</h1>')
        self.la_heading.setAlignment(QtCore.Qt.AlignHCenter)

        self.la_patchnotes = QtWidgets.QLabel(self)
        self.la_patchnotes.setGeometry(QtCore.QRect(20, 40, self.width() - 20, self.height() - 40))
        self.la_patchnotes.setText(text)
        self.la_patchnotes.setFont(font)

        self.show()

    @QtCore.pyqtSlot(bool)
    def closeEvent(self, event):
        """ Overriding close event. Otherwise it closes the app when it's minimized """
        event.ignore()
        self.hide()


class SortingQLabel(QtWidgets.QLabel):
    def __init__(self, parent, reverse=False):
        super(SortingQLabel, self).__init__(parent)
        self.p = parent
        self.defaultreverse = not reverse
        self.reverse = self.defaultreverse

    active = dict()
    clicked = QtCore.pyqtSignal()

    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()

    def setText(self, text):
        self.value = text
        super().setText(text)

    def activate(self):
        self.reverse = not self.reverse
        # Not the best way of doing it as a combination of AligmentFlags will not be equal
        if super().alignment() == QtCore.Qt.AlignRight:
            super().setText(('▼' if self.reverse else '▲') + self.value)
        elif super().alignment() == QtCore.Qt.AlignLeft:
            super().setText(self.value + ('▼' if self.reverse else '▲'))
        else:
            super().setText('   ' + self.value + ('▼' if self.reverse else '▲'))
        # Hmmm
        if self.p.p in SortingQLabel.active:
            if not SortingQLabel.active[self.p.p] == self:
                SortingQLabel.active[self.p.p].deactivate()
        SortingQLabel.active[self.p.p] = self

    def deactivate(self):
        super().setText(self.value)
        self.reverse = self.defaultreverse
