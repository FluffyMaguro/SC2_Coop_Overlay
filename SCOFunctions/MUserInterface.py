import os
import sys
import time
import traceback
import subprocess

from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets

import SCOFunctions.MainFunctions as MF
from SCOFunctions.MFilePath import innerPath, truePath
from SCOFunctions.MLogging import logclass
from SCOFunctions.MainFunctions import show_overlay
from SCOFunctions.SC2Dictionaries import prestige_names, CommanderMastery


logger = logclass('UI','INFO')


def find_file(file):
    new_path = os.path.abspath(file)
    logger.info(f'Finding file {new_path}')
    subprocess.Popen(f'explorer /select,"{new_path}"')


class CommKillFractions(QtWidgets.QWidget):
    """Widget for fractional kills of commanders """
    def __init__(self, analysis, parent=None):
        super().__init__(parent)
        self.setGeometry(QtCore.QRect(600, 10, 700, 500))
        

        self.desc = QtWidgets.QLabel(self)
        self.desc.setGeometry(QtCore.QRect(0, 0, 300, 20))
        self.desc.setText('<b>Typical commander kill fractions</>')

        data = analysis['CommanderData'].copy()
        data = {k:v for k,v in sorted(data.items(), key=lambda x:x[1]['KillFraction'], reverse=True)}
        an = data.pop('any')
        data['Average'] = an

        self.elements = dict()
        self.elements['main_heading'] = QtWidgets.QLabel(self)
        self.elements['main_heading'].setGeometry(QtCore.QRect(100, 22, 150, 17))
        self.elements['main_heading'].setText('Main')

        self.elements['ally_heading'] = QtWidgets.QLabel(self)
        self.elements['ally_heading'].setGeometry(QtCore.QRect(150, 22, 150, 17))
        self.elements['ally_heading'].setText('Ally')

        for idx, commander in enumerate(data):
            self.elements[(commander, 'name')] = QtWidgets.QLabel(self)
            self.elements[(commander, 'name')].setGeometry(QtCore.QRect(0, idx*17+40, 150, 17))
            self.elements[(commander, 'name')].setText(commander)

            self.elements[(commander, 'main')] = QtWidgets.QLabel(self)
            self.elements[(commander, 'main')].setGeometry(QtCore.QRect(100, idx*17+40, 150, 17))
            self.elements[(commander, 'main')].setText(f"{100*data[commander]['KillFraction']:.0f}%")

            self.elements[(commander, 'ally')] = QtWidgets.QLabel(self)
            self.elements[(commander, 'ally')].setGeometry(QtCore.QRect(150, idx*17+40, 150, 17))
            self.elements[(commander, 'ally')].setText(f"{100*analysis['AllyCommanderData'].get(commander if commander != 'Average' else 'any',{'KillFraction':0})['KillFraction']:.0f}%")

            style = ''
            if not idx%2:
                style = 'background-color: #f1f1f1;'
            if commander == 'Average':
                style += ' font-weight: bold'
            if style != '':
                self.elements[(commander, 'name')].setStyleSheet(style)
                self.elements[(commander, 'main')].setStyleSheet(style)
                self.elements[(commander, 'ally')].setStyleSheet(style)


        self.show()



class RegionStats(QtWidgets.QWidget):
    """Widget for region stats """
    def __init__(self, region, fdict, y, parent=None, bold=False, line=False,  bg=False):
        super().__init__(parent)
        self.setGeometry(QtCore.QRect(15, y+20, 700, 20))

        xspacing = 65
        width = 120

        if bg:
            self.bg = QtWidgets.QFrame(self)
            self.bg.setGeometry(QtCore.QRect(35, 2, self.width()-30, 18))
            self.bg.setAutoFillBackground(True)

        self.la_name = QtWidgets.QLabel(self)
        self.la_name.setGeometry(QtCore.QRect(0, 0, width, 20))
        self.la_name.setText(str(region))

        # Frequency
        self.la_frequency = QtWidgets.QLabel(self)
        self.la_frequency.setGeometry(QtCore.QRect(1*xspacing+2, 0, width, 20))
        if isinstance(fdict['frequency'], str):
            self.la_frequency.setText(fdict['frequency'])
        else:
            self.la_frequency.setText(f"{100*fdict['frequency']:.0f}%")

        # Wins
        self.la_wins = QtWidgets.QLabel(self)
        self.la_wins.setGeometry(QtCore.QRect(2*xspacing, 0, width, 20))
        self.la_wins.setText(str(fdict['Victory']))

        # Losses
        self.la_losses = QtWidgets.QLabel(self)
        self.la_losses.setGeometry(QtCore.QRect(3*xspacing, 0, width, 20))
        self.la_losses.setText(str(fdict['Defeat']))

        # Winrate
        self.la_winrate = QtWidgets.QLabel(self)
        self.la_winrate.setGeometry(QtCore.QRect(4*xspacing, 0, width, 20))
        if isinstance(fdict['winrate'], str):
            self.la_winrate.setText(fdict['winrate'])
        else:
            self.la_winrate.setText(f"{100*fdict['winrate']:.0f}%")

        # Ascension level
        self.la_asc = QtWidgets.QLabel(self)
        self.la_asc.setGeometry(QtCore.QRect(5*xspacing+20, 0, width, 20))
        self.la_asc.setText(str(fdict['max_asc']))

        # Tried prestiges 4/18*3, tooltip
        self.la_prestiges = QtWidgets.QLabel(self)
        self.la_prestiges.setGeometry(QtCore.QRect(6*xspacing+60, 0, width, 20))
        if isinstance(fdict['prestiges'], str):
            self.la_prestiges.setText(fdict['prestiges'])
        else:
            total = 0
            text = ''
            for idx,co in enumerate(fdict['prestiges']):
                total += len(fdict['prestiges'][co])
                prest = {str(i) for i in fdict['prestiges'][co]}
                prest = ', '.join(prest)
                if idx+1 != len(fdict['prestiges']):
                    text += f"{co}: {prest}\n"
                else:
                    text += f"{co}: {prest}"

            self.la_prestiges.setText(f"{total}/54")
            self.la_prestiges.setToolTip(text)

        # Maxed commanders list
        self.la_commanders = QtWidgets.QLabel(self)
        self.la_commanders.setGeometry(QtCore.QRect(7*xspacing+95, 0, 160, 20))
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

        for item in {self.la_name, self.la_frequency, self.la_wins, self.la_losses, self.la_winrate, self.la_asc, self.la_prestiges, self.la_commanders}:
            item.setAlignment(QtCore.Qt.AlignCenter)

        if line:
            self.line = QtWidgets.QFrame(self)
            self.line.setGeometry(QtCore.QRect(34, 19, 660, 2))
            self.line.setFrameShape(QtWidgets.QFrame.HLine)
            self.line.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.show()


class CommanderStats(QtWidgets.QWidget):
    """ Widget for detailed stats for allied commander (mastery, prestige)"""
    def __init__(self, commander, fanalysis, parent=None):
        super().__init__(parent)
        self.setGeometry(QtCore.QRect(470, 50, 500, 410))

        # Background
        self.fr_bg = QtWidgets.QLabel(self)
        self.fr_bg.setGeometry(QtCore.QRect(0, 0, self.width()-20, 87))
        self.fr_bg.setStyleSheet(f'background-color: black;')

        image_file = truePath(f'Layouts/Commanders/{commander}.png')
        if os.path.isfile(image_file):
            pixmap = QtGui.QPixmap(image_file)
            pixmap = pixmap.scaled(self.fr_bg.width(), self.fr_bg.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
            self.fr_bg.setPixmap(pixmap)
       
        # Commander name
        self.la_name = QtWidgets.QLabel(self)
        self.la_name.setGeometry(QtCore.QRect(0, 0, self.width()-40, 87))
        self.la_name.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.la_name.setText(str(commander))
        self.la_name.setStyleSheet(f'font-weight: bold; font-size: 30px; color: white;')
        shadow = QtWidgets.QGraphicsDropShadowEffect() 
        shadow.setBlurRadius(1)
        shadow.setOffset(2)
        self.la_name.setGraphicsEffect(shadow) 

        # Frequency
        self.la_frequency = QtWidgets.QLabel(self)
        self.la_frequency.setGeometry(QtCore.QRect(230, 98, 150, 25))
        self.la_frequency.setText(f"Frequency: <b>{100*fanalysis[commander]['Frequency']:.1f}%</b>")
        self.la_frequency.setAlignment(QtCore.Qt.AlignRight)

        # APM
        self.la_apm = QtWidgets.QLabel(self)
        self.la_apm.setGeometry(QtCore.QRect(300, 98, 180, 25))
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
            fill = fill if (idx%2 == 1 or idx==0) else '<br>'+fill
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

        self.setGeometry(QtCore.QRect(485, 48, 485, 380))

        # Map frame
        self.fr_map = QtWidgets.QFrame(self)
        self.fr_map.setGeometry(QtCore.QRect(0, 2, 473, 87))

        # Map name
        self.la_name = QtWidgets.QLabel(self)
        self.la_name.setGeometry(QtCore.QRect(15, 20, 460, 40))
        self.la_name.setStyleSheet('font-weight: bold; font-size: 24px; color: white')
        shadow = QtWidgets.QGraphicsDropShadowEffect() 
        shadow.setBlurRadius(1)
        shadow.setOffset(2)
        self.la_name.setGraphicsEffect(shadow) 

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
        self.bt_findfile.setGeometry(QtCore.QRect(10, 325, 75, 23))       
        self.bt_findfile.setText("Find file")

        # Show overlay button
        self.bt_showoverlay = QtWidgets.QPushButton(self)
        self.bt_showoverlay.setGeometry(QtCore.QRect(95, 325, 81, 23))
        self.bt_showoverlay.setText("Show overlay")

        # Date & difficulty
        self.la_date_difficulty = QtWidgets.QLabel(self)
        self.la_date_difficulty.setGeometry(QtCore.QRect(265, 385, 200, 20))
        self.la_date_difficulty.setAlignment(QtCore.Qt.AlignRight)
        self.la_date_difficulty.setEnabled(False)

        for item in {self.la_name, self.la_time_race, self.la_p1name, self.la_p1apm, self.la_p1masteries,self.la_p2name, self.la_p2apm, self.la_p2masteries, self.la_date_difficulty}:
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
            length = time.strftime('%M:%S',time.gmtime(fdict['length']))
        else:
            length = time.strftime('%H:%M:%S',time.gmtime(fdict['length']))
        self.la_time_race.setText(f"{length} | {fdict.get('enemy_race','')}")

        if fdict['players'][0]['handle'] in handles:
            p1, p2 = 0, 1
        else:
            p1, p2 = 1, 0

        prestige = prestige_names[fdict['players'][p1]['commander']][fdict['players'][p1]['prestige']]
        self.la_p1name.setText(f"<h3>{fdict['players'][p1]['name']} ({fdict['players'][p1]['commander']})<br>{prestige} (P{fdict['players'][p1]['prestige']})</h3>")
        self.la_p1apm.setText(f"{fdict['players'][p1]['apm']} APM")
        self.la_p1masteries.setText(self.format_mastery(fdict['players'][p1]['commander'],fdict['players'][p1]['masteries']))

        prestige = prestige_names[fdict['players'][p2]['commander']][fdict['players'][p2]['prestige']]
        self.la_p2name.setText(f"<h3>{fdict['players'][p2]['name']} ({fdict['players'][p2]['commander']})<br>{prestige} (P{fdict['players'][p2]['prestige']})</h3>") 
        self.la_p2apm.setText(f"{fdict['players'][p2]['apm']} APM")
        self.la_p2masteries.setText(self.format_mastery(fdict['players'][p2]['commander'],fdict['players'][p2]['masteries']))

        try:
            self.bt_findfile.clicked.disconnect()
            self.bt_showoverlay.clicked.disconnect()
        except:
            pass

        self.bt_findfile.clicked.connect(lambda: find_file(fdict['file']))
        self.bt_showoverlay.clicked.connect(lambda: show_overlay(fdict['file']))

        self.la_date_difficulty.setText(f"{fdict['difficulty']} | {fdict['date'].replace(':','-',2).replace(':',' ',1)}")
        self.show()


    @staticmethod
    def format_mastery(commander:str, masterylist:list):
        text = ''
        for idx, mastery in enumerate(masterylist):
            fill = '' if mastery > 9 else '  '
            style = ' style="color:#aaa"' if mastery == 0 else ''
            text += f"<span{style}>{fill}{mastery}  {CommanderMastery[commander][idx]}</span><br>" 
        return text


class CommanderEntry(QtWidgets.QWidget):
    """Custom widget for ally commander entry in stats""" 
    def __init__(self, commander, frequency, wins, losses, winrate, apm, y, button=True, bold=False, bg=False, bgcolor="#f1f1f1", parent=None):
        super().__init__(parent)

        self.setGeometry(QtCore.QRect(15, y, 450, 25))
        
        # Button/label
        if button:
            self.bt_button = QtWidgets.QPushButton(self)
            self.bt_button.setGeometry(QtCore.QRect(0, 0, 150, 25))
        else:
            self.bt_button = QtWidgets.QLabel(self)
            self.bt_button.setGeometry(QtCore.QRect(0, 0, 150, 20))
            self.bt_button.setAlignment(QtCore.Qt.AlignCenter)
        self.bt_button.setText(commander)

        # Frequency
        self.la_frequency = QtWidgets.QLabel(self)
        self.la_frequency.setGeometry(QtCore.QRect(150, 0, 70, 20))
        self.la_frequency.setAlignment(QtCore.Qt.AlignCenter)
        self.la_frequency.setToolTip('Commander frequency (corrected for your commander choices)')
        self.la_frequency.setText(str(frequency))

        # Wins
        self.la_wins = QtWidgets.QLabel(self)
        self.la_wins.setGeometry(QtCore.QRect(210, 0, 70, 20))
        self.la_wins.setAlignment(QtCore.Qt.AlignCenter)
        self.la_wins.setText(str(wins))
      
        # Losses
        self.la_losses = QtWidgets.QLabel(self)
        self.la_losses.setGeometry(QtCore.QRect(275, 0, 55, 20))
        self.la_losses.setAlignment(QtCore.Qt.AlignCenter)  
        self.la_losses.setText(str(losses))

        # Winrate
        self.la_winrate = QtWidgets.QLabel(self)
        self.la_winrate.setGeometry(QtCore.QRect(328, 0, 55, 20))
        self.la_winrate.setAlignment(QtCore.Qt.AlignCenter)  
        self.la_winrate.setText(str(winrate))

        # Apm
        self.la_apm = QtWidgets.QLabel(self)
        self.la_apm.setGeometry(QtCore.QRect(380, 0, 50, 20))
        self.la_apm.setAlignment(QtCore.Qt.AlignCenter)  
        self.la_apm.setToolTip('Median APM')
        self.la_apm.setText(str(apm))


        style = ''
        if bold:
            style += 'font-weight: bold;'
            self.bt_button.setStyleSheet('font-weight: bold')
        if bg:
            style += f'background-color: {bgcolor}'

        for item in {self.la_frequency, self.la_wins, self.la_losses, self.la_winrate, self.la_apm}:
            item.setStyleSheet(style)

        self.show()


class MapEntry(QtWidgets.QWidget):
    """Custom widget for map entry in stats""" 
    def __init__(self, parent, y, name, time_fastest, time_average, wins, losses, frequency, button=True, bold=False, bg=False, bgcolor="#f1f1f1"):
        super().__init__(parent)

        self.setGeometry(QtCore.QRect(7, y-6, parent.width()-10, 40))
        if bold:
            self.setStyleSheet('font-weight: bold')
        
        # Button/label
        self.bt_button = QtWidgets.QPushButton(self) if button else QtWidgets.QLabel(self)
        self.bt_button.setGeometry(QtCore.QRect(0, 0, 150, 25))
        if not button:
            self.bt_button.setAlignment(QtCore.Qt.AlignCenter)
            self.bt_button.setGeometry(QtCore.QRect(0, 0, 150, 20))
        
        if 'Lock' in name and 'Load' in name:
            name = "Lock and Load"
        self.bt_button.setText(name)

        # Average time
        self.la_average = QtWidgets.QLabel(self)
        
        self.la_average.setAlignment(QtCore.Qt.AlignCenter)
        self.la_average.setToolTip('Average victory time')
        time_average = time_average if time_average != 999999 else '–'
        if isinstance(time_average, int) or isinstance(time_average, float):
            self.la_average.setGeometry(QtCore.QRect(150, 0, 66, 20))
            if time_average < 3600:
                self.la_average.setText(time.strftime('%M:%S',time.gmtime(time_average)))
            else:
                self.la_average.setText(time.strftime('%H:%M:%S',time.gmtime(time_average)))

        elif time_average == '–':
            self.la_average.setGeometry(QtCore.QRect(150, 0, 66, 20))
        else:
            self.la_average.setGeometry(QtCore.QRect(147, 0, 70, 20))
            self.la_average.setText(time_average)
            

        # Fastest time
        self.la_fastest = QtWidgets.QLabel(self)
        self.la_fastest.setGeometry(QtCore.QRect(201, 0, 70, 20))
        self.la_fastest.setAlignment(QtCore.Qt.AlignCenter)
        self.la_fastest.setToolTip('Fastest victory time')
        time_fastest = time_fastest if time_fastest != 999999 else '–'
        if isinstance(time_fastest, int) or isinstance(time_fastest, float):
            if time_fastest < 3600:
                self.la_fastest.setText(time.strftime('%M:%S',time.gmtime(time_fastest)))
            else:
                self.la_fastest.setText(time.strftime('%H:%M:%S',time.gmtime(time_fastest)))
        else:
            self.la_fastest.setText(time_fastest)

        # Frequency    
        self.la_frequency = QtWidgets.QLabel(self)
        self.la_frequency.setGeometry(QtCore.QRect(250, 0, 70, 20))
        self.la_frequency.setAlignment(QtCore.Qt.AlignCenter)  
        if isinstance(frequency, str):
            self.la_frequency.setText(frequency)
        else:
            self.la_frequency.setText(f'{100*frequency:.0f}%')

        # Wins
        self.la_wins = QtWidgets.QLabel(self)
        self.la_wins.setGeometry(QtCore.QRect(303, 0, 50, 20))
        self.la_wins.setAlignment(QtCore.Qt.AlignCenter)  
        self.la_wins.setText(str(wins))

        # Losses
        self.la_losses = QtWidgets.QLabel(self)
        self.la_losses.setGeometry(QtCore.QRect(346, 0, 54, 20))
        self.la_losses.setAlignment(QtCore.Qt.AlignCenter)  
        self.la_losses.setText(str(losses))

        # Winrate
        self.la_winrate = QtWidgets.QLabel(self)
        self.la_winrate.setGeometry(QtCore.QRect(400, 0, 50, 20))
        self.la_winrate.setAlignment(QtCore.Qt.AlignCenter)  
        if isinstance(wins, str) or isinstance(losses, str):
            winrate = 'Winrate'
        else:
            winrate = '-'
            if wins or losses > 0:
                winrate = f"{100*wins/(wins+losses):.0f}%"
        self.la_winrate.setText(winrate)

        self.show()

        if bg:
            for item in {self.la_average, self.la_fastest, self.la_frequency, self.la_wins, self.la_losses, self.la_winrate}:
                item.setStyleSheet(f'background-color: {bgcolor}')


class DifficultyEntry(QtWidgets.QWidget):
    """Custom widget for difficulty entry in stats"""

    def __init__(self, name, wins, losses, winrate, x, y, bold=False, line=False, bg=False, bgcolor="#f1f1f1", parent=None):
        super().__init__(parent)

        self.setGeometry(QtCore.QRect(x, y+150, 300, 40))

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

        style = ''

        if bold:
            style += 'font-weight: bold;'

        if bg:
            style += f'background-color: {bgcolor}'

        self.setStyleSheet(style)

        if line:
            self.line = QtWidgets.QFrame(self)
            self.line.setGeometry(QtCore.QRect(0, 30, 235, 2))
            self.line.setFrameShape(QtWidgets.QFrame.HLine)
            self.line.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.show()


class GameEntry:
    """ 
    Class for UI elements in games tab. 
    It takes `replay_dict` generated by s2parser. 
    """

    def __init__(self, replay_dict, handles, parent):
        self.mapname = replay_dict['map_name']
        self.result = replay_dict['result']
        self.difficulty = replay_dict['ext_difficulty']
        self.enemy = replay_dict['enemy_race']
        self.length = replay_dict['form_alength']
        self.file = replay_dict['file']
        self.date = replay_dict['date'][:10].replace(':','-') + ' ' + replay_dict['date'][11:16]
        self.chat_showing = False
        self.message_count = len(replay_dict['messages'])

        if replay_dict['players'][1]['handle'] in handles:
            self.p1_name = replay_dict['players'][1]['name']
            self.p1_commander = replay_dict['players'][1]['commander']
            self.p1_handle = replay_dict['players'][1]['handle']
            self.p2_name = replay_dict['players'][2].get('name','')
            self.p2_commander = replay_dict['players'][2].get('commander')
            self.p2_handle = replay_dict['players'][2].get('handle','')
        else:
            self.p1_name = replay_dict['players'][2].get('name')
            self.p1_commander = replay_dict['players'][2].get('commander')
            self.p1_handle = replay_dict['players'][2].get('handle')
            self.p2_name = replay_dict['players'][1]['name']
            self.p2_commander = replay_dict['players'][1]['commander']
            self.p2_handle = replay_dict['players'][1]['handle']


        height = 30
        line_spacing = 7

        self.widget = QtWidgets.QWidget(parent)
        self.widget.setGeometry(QtCore.QRect(0, 0, 931, height))
        self.widget.setMinimumHeight(height)
        self.widget.setMaximumHeight(height)

        self.line = QtWidgets.QFrame(self.widget)
        self.line.setGeometry(QtCore.QRect(10, 0, 921, 2))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)        

        self.la_mapname = QtWidgets.QLabel(self.widget)
        self.la_mapname.setGeometry(QtCore.QRect(20, line_spacing, 125, 21))
        self.la_mapname.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.la_mapname.setText(self.mapname)

        self.la_result = QtWidgets.QLabel(self.widget)
        self.la_result.setGeometry(QtCore.QRect(135, line_spacing, 50, 21))
        self.la_result.setAlignment(QtCore.Qt.AlignCenter)
        self.la_result.setText(self.result)

        self.la_p1 = QtWidgets.QLabel(self.widget)
        self.la_p1.setGeometry(QtCore.QRect(160, line_spacing, 200, 21))
        self.la_p1.setAlignment(QtCore.Qt.AlignCenter)
        self.la_p1.setText(f'{self.p1_name} ({self.p1_commander})')

        self.la_p2 = QtWidgets.QLabel(self.widget)
        self.la_p2.setGeometry(QtCore.QRect(295, line_spacing, 200, 21))
        self.la_p2.setAlignment(QtCore.Qt.AlignCenter)
        self.la_p2.setText(f'{self.p2_name} ({self.p2_commander})')

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
        self.la_chat.setGeometry(QtCore.QRect(20, 35, 500, 10+14*self.message_count))
        self.la_chat.setAlignment(QtCore.Qt.AlignTop)

        testplayer = 2 if replay_dict['players'][1]['handle'] in handles else 1

        text = ''
        for message in replay_dict['messages']:
            color = '#338F00' if message['player'] == testplayer else 'blue'
            if message['time'] >= 3600:
                t = time.strftime('%H:%M:%S', time.gmtime(message['time']))
            else:
                t = time.strftime('%M:%S', time.gmtime(message['time']))
            style = f'style="color: {color}"'
            text += f"<span {style}>{t}&nbsp;&nbsp;<b>{replay_dict['players'][message['player']]['name']}</b>:&nbsp;&nbsp;{message['text']}</span><br>"

        self.la_chat.setText(text)
        self.la_chat.hide()

        # Styling
        for item in {self.la_chat, self.la_mapname, self.la_result, self.la_p1, self.la_p2, self.la_enemy, self.la_length, self.la_difficulty, self.la_date}:
            item.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            if self.result == 'Defeat':
                item.setStyleSheet('color: red')


    def show_chat(self):
        """ Shows/hides chat """       
        if self.chat_showing:
            self.chat_showing = False
            height = 30
            self.la_chat.hide()
        else:
            self.chat_showing = True
            height = 30 + (10 + 14*self.message_count) if self.message_count > 0 else 50
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

        height = 30
        line_spacing = 7

        self.widget = QtWidgets.QWidget(parent)
        self.widget.setGeometry(QtCore.QRect(0, 0, 931, height))
        self.widget.setMinimumHeight(height)
        self.widget.setMaximumHeight(height)

        self.line = QtWidgets.QFrame(self.widget)
        self.line.setGeometry(QtCore.QRect(10, 0, 921, 2))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.la_name = QtWidgets.QLabel(self.widget)
        self.la_name.setGeometry(QtCore.QRect(40, line_spacing, 150, 21))
        self.la_name.setText(self.name)

        self.la_wins = QtWidgets.QLabel(self.widget)
        self.la_wins.setGeometry(QtCore.QRect(170, line_spacing, 31, 21))
        self.la_wins.setAlignment(QtCore.Qt.AlignCenter)

        self.la_losses = QtWidgets.QLabel(self.widget)
        self.la_losses.setGeometry(QtCore.QRect(230, line_spacing, 41, 21))
        self.la_losses.setAlignment(QtCore.Qt.AlignCenter)

        self.la_winrate = QtWidgets.QLabel(self.widget)
        self.la_winrate.setGeometry(QtCore.QRect(300, line_spacing, 51, 21))
        self.la_winrate.setAlignment(QtCore.Qt.AlignCenter)

        self.la_apm = QtWidgets.QLabel(self.widget)
        self.la_apm.setGeometry(QtCore.QRect(370, line_spacing, 51, 21))
        self.la_apm.setAlignment(QtCore.Qt.AlignCenter)
        self.la_apm.setToolTip("Median APM")

        self.la_commander = QtWidgets.QLabel(self.widget)
        self.la_commander.setGeometry(QtCore.QRect(425, line_spacing, 81, 21))
        self.la_commander.setAlignment(QtCore.Qt.AlignCenter)
        self.la_commander.setToolTip("The most played commander")

        self.la_frequency = QtWidgets.QLabel(self.widget)
        self.la_frequency.setGeometry(QtCore.QRect(510, line_spacing, 51, 21))
        self.la_frequency.setAlignment(QtCore.Qt.AlignCenter)
        self.la_frequency.setToolTip("The most played commander frequency")

        self.ed_note = QtWidgets.QLineEdit(self.widget)
        self.ed_note.setGeometry(QtCore.QRect(580, line_spacing, 300, 21))
        self.ed_note.setAlignment(QtCore.Qt.AlignCenter)
        self.ed_note.setStyleSheet('color: #444')
        if not self.note in {None,''}:
            self.ed_note.setText(self.note)

        # This is necessary only sometimes (when the user is looking at the tab while its updating )
        for item in {self.widget, self.line, self.la_name, self.la_wins, self.la_losses, self.la_winrate, self.ed_note}:
            item.show()

        for item in {self.la_name, self.la_wins, self.la_losses, self.la_winrate}:
            item.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)


        self.update_winrates(winrate_data)


    def get_note(self):
        return self.ed_note.text()


    def show(self):
        self.widget.show()


    def hide(self):
        self.widget.hide()


    def update_winrates(self, data):
        """ Updates winrate for the player. """
        self.wins = data[0]
        self.losses = data[1]
        self.winrate = 100*self.wins/(self.wins+self.losses)

        self.la_wins.setText(str(self.wins))
        self.la_losses.setText(str(self.losses))
        self.la_winrate.setText(f'{self.winrate:.0f}%')
        self.la_apm.setText(f'{data[2]:.0f}')
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


    @QtCore.pyqtSlot()
    def run(self):
        """ Runs the function and emits signals (error, result, finished) """
        try:
            try:
                result = self.fn(*self.args, **self.kwargs)
            except:
                logger.error(traceback.format_exc())
                exctype, value = sys.exc_info()[:2]
                self.signals.error.emit((exctype, value, traceback.format_exc()))
            else:
                self.signals.result.emit(result)
            finally:
                self.signals.finished.emit()
        except RuntimeError:
            logger.debug('Error with pyqt thread. The app likely closed.')
        except:
            logger.error(traceback.format_exc())


class CustomKeySequenceEdit(QtWidgets.QKeySequenceEdit):
    def __init__(self, parent=None):
        super(CustomKeySequenceEdit, self).__init__(parent)
 
    def keyPressEvent(self, QKeyEvent):
        super(CustomKeySequenceEdit, self).keyPressEvent(QKeyEvent)
        value = self.keySequence()
        self.setKeySequence(QtGui.QKeySequence(value))


class CustomQTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None, settings=dict()):
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

        self.settings = settings


    @QtCore.pyqtSlot(bool)    
    def closeEvent(self, event):
        """ Overriding close event and minimizing instead """
        event.ignore()
        self.hide()
        self.show_minimize_message()


    def format_close_message(self):
        """ Shows few hotkeys in the notification area"""
        text = ''
        setting_dict = {"hotkey_show/hide":"Show/Hide","hotkey_newer":"Newer replay","hotkey_older":"Older replay"}
        for key in setting_dict:
            if key in self.settings and self.settings[key] != '':
                text += f"\n{self.settings[key]} → {setting_dict[key]}"
        return text


    def show_minimize_message(self, message=''):
        self.tray_icon.showMessage(
                "StarCraft Co-op Overlay",
                f"App was minimized into the tray{self.format_close_message()}",
                QtGui.QIcon(innerPath('src/OverlayIcon.ico')),
                2000
            )


    def tray_activated(self, reason):
        """ Hides/shows main window when the tray icon is double clicked """
        if reason == 2:
            if self.isVisible():
                self.hide()
            else:
                #Change flags briefly to bring to front
                self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                self.show()
                self.setWindowFlags(QtCore.Qt.Window)
                self.show()


class CustomWebView(QtWebEngineWidgets.QWebEngineView):
    """ Expanding this class to add javascript after page is loaded. This is could be used to distinquish main overlay from other overlays (e.g. in OBS)"""
    def __init__(self,  parent=None):
        super().__init__(parent)
        self.loadFinished.connect(self.on_load_finished)


    @QtCore.pyqtSlot(bool)
    def on_load_finished(self,ok):
        if ok:
            self.page().runJavaScript(f"do_not_use_websocket = true;")
            MF.resend_init_message()
