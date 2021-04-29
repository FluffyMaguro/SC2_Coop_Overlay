"""
Main module for StarCraft II Co-op Overlay.

Causal chain:
Setup -> Load Settings -> UI
                       -> Server manager (thread)
                       -> Twitch bot (thread)
                       -> Check replays (loop of threads)
                       -> Mass replay analysis -> Player winrates (thread)
                                               -> Generate stats (function)
"""
import os
import sys
import json
import shutil
import platform
import threading
import traceback
import urllib.request
from functools import partial
from datetime import datetime

import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets

import SCOFunctions.MUserInterface as MUI
import SCOFunctions.MainFunctions as MF
import SCOFunctions.HelperFunctions as HF
import SCOFunctions.MassReplayAnalysis as MR
import SCOFunctions.Tabs as Tabs
from SCOFunctions.MChatWidget import ChatWidget
from SCOFunctions.MLogging import logclass, catch_exceptions
from SCOFunctions.MFilePath import truePath, innerPath
from SCOFunctions.MTwitchBot import TwitchBot
from SCOFunctions.FastExpand import FastExpandSelector
from SCOFunctions.MSystemInfo import SystemInfo
from SCOFunctions.MTheming import set_dark_theme, MColors
from SCOFunctions.MDebugWindow import DebugWindow
from SCOFunctions.Settings import Setting_manager as SM

logger = logclass('SCO', 'INFO')
logclass.FILE = truePath("Logs.txt")

APPVERSION = 236


class Signal_Manager(QtCore.QObject):
    """ 
    Small object for emiting signals.

    Through this object non-PyQt threads can safely interact with PyQt.
    Threads can emit signals, e.g.: signal_manager.showHidePerfOverlay.emit() and
    and some method connected to this signal will be called in the primary
    PyQt thread.
    
    """
    showHidePerfOverlay = QtCore.pyqtSignal()


class MultipleInstancesRunning(Exception):
    """ Custom exception for multiple instance of the app running"""
    pass


class UI_TabWidget(object):
    def setupUI(self, TabWidget):
        TabWidget.setWindowTitle(f"StarCraft Co-op Overlay (v{str(APPVERSION)[0]}.{str(APPVERSION)[1:]})")
        TabWidget.setWindowIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        TabWidget.setFixedSize(980, 610)
        TabWidget.tray_icon.setToolTip(f'StarCraft Co-op Overlay')

        self.signal_manager = Signal_Manager()
        self.signal_manager.showHidePerfOverlay.connect(self.show_hide_performance_overlay)

        # Tabs
        self.TAB_Main = Tabs.MainTab(self, APPVERSION)
        self.TAB_Players = Tabs.PlayerTab(self, TabWidget)
        self.TAB_Games = Tabs.GameTab(self, TabWidget)
        self.TAB_Stats = Tabs.StatsTab(self)
        self.TAB_Randomizer = Tabs.RngTab(self)
        self.TAB_TwitchBot = Tabs.TwitchTab(self)
        self.TAB_Resources = Tabs.ResourceTab(self)
        self.TAB_Links = Tabs.LinkTab()

        # Add tabs to the widget
        TabWidget.addTab(self.TAB_Main, "Settings")
        TabWidget.addTab(self.TAB_Games, "Games")
        TabWidget.addTab(self.TAB_Players, "Players")
        TabWidget.addTab(self.TAB_Stats, "Statistics")
        TabWidget.addTab(self.TAB_Randomizer, "Randomizer")
        TabWidget.addTab(self.TAB_TwitchBot, "Twitch")
        TabWidget.addTab(self.TAB_Resources, "Performance")
        TabWidget.addTab(self.TAB_Links, "Links")

        QtCore.QMetaObject.connectSlotsByName(TabWidget)

        if not HF.isWindows():
            self.TAB_Main.CH_StartWithWindows.setChecked(False)
            self.TAB_Main.CH_StartWithWindows.setEnabled(False)

        self.FastExpandSelector = None

    def loadSettings(self):
        """ Loads settings from the config file if there is any, updates UI elements accordingly"""
        self.downloading = False

        SM.load_settings(truePath('Settings.json'))

        # Check for multiple instances
        if SM.settings['check_for_multiple_instances'] and HF.isWindows():
            if HF.app_running_multiple_instances():
                logger.error('App running at multiple instances. Closing!')
                raise MultipleInstancesRunning

        # Update fix font size
        font = QtGui.QFont()
        if HF.isWindows():
            font.fromString(f"MS Shell Dlg 2,{8.25*SM.settings['font_scale']},-1,5,50,0,0,0,0,0")
        else:
            font.setPointSize(font.pointSize() * SM.settings['font_scale'])
        app.setFont(font)

        # Dark theme
        if SM.settings['dark_theme']:
            set_dark_theme(self, app, TabWidget, APPVERSION)

        # Check if account directory valid, update if not
        SM.settings['account_folder'] = HF.get_account_dir(SM.settings['account_folder'])

        # Screenshot folder
        if SM.settings['screenshot_folder'] in {None, ''} or not os.path.isdir(SM.settings['screenshot_folder']):
            SM.settings['screenshot_folder'] = os.path.normpath(os.path.join(os.path.expanduser('~'), 'Desktop'))

        self.updateUI()
        self.check_for_updates()

        if SM.settings['start_minimized']:
            TabWidget.hide()
            TabWidget.show_minimize_message()
        else:
            TabWidget.show()

        # Check write permissions
        self.write_permissions = HF.write_permission_granted()
        if not self.write_permissions:
            self.sendInfoMessage('Permission denied. Add an exception to your anti-virus for this folder. Sorry', color=MColors.msg_failure)

        logclass.LOGGING = SM.settings['enable_logging'] if self.write_permissions else False

        self.manage_keyboard_threads()

        self.full_analysis_running = False

        # Delete install bat if it's there. Show patchnotes
        if os.path.isfile(truePath('install.bat')):
            os.remove(truePath('install.bat'))
            self.show_patchnotes()

    def show_patchnotes(self):
        """ Shows a widget with the lastest patchnotes.
        Usually shown only after an update (after deleting install.bat)"""
        try:
            file = innerPath('src/patchnotes.json')
            if not os.path.isfile(file):
                return

            with open(file, 'r') as f:
                patchnotes = json.load(f)

            patchnotes = patchnotes.get(str(APPVERSION), None)

            if patchnotes is None:
                return
            if len(patchnotes) == 0:
                return

            self.WD_patchnotes = MUI.PatchNotes(APPVERSION, patchnotes=patchnotes, icon=QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        except Exception:
            logger.error(traceback.format_exc())

    def check_for_updates(self):
        """ Checks for updates and changes UI accordingly"""
        self.new_version = HF.new_version(APPVERSION)

        if not self.new_version:
            return

        self.TAB_Main.LA_Version.setText('New version available!')

        # Create button
        self.BT_NewUpdate = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_NewUpdate.setGeometry(QtCore.QRect(351, 400, 157, 40))
        self.BT_NewUpdate.setText('Download update')
        self.BT_NewUpdate.setStyleSheet('font-weight: bold; background-color: #5BD3C4; color: black')
        self.BT_NewUpdate.clicked.connect(self.start_download)
        self.BT_NewUpdate.show()

        # Check if it's already downloaded
        save_path = truePath(f'Updates\\{self.new_version.split("/")[-1]}')

        if not HF.isWindows():
            self.sendInfoMessage('Update available', color=MColors.msg_success)
            return

        if os.path.isfile(save_path):
            self.update_is_ready_for_install()
        else:
            self.PB_download = QtWidgets.QProgressBar(self.TAB_Main)
            self.PB_download.setGeometry(21, 569, 830, 10)
            self.PB_download.hide()

    def start_download(self):
        """ Starts downloading an update"""
        if self.downloading:
            return

        self.downloading = True
        self.BT_NewUpdate.setText('Downloading')
        self.BT_NewUpdate.setEnabled(False)
        self.BT_NewUpdate.setStyleSheet('font-weight: bold; background-color: #CCCCCC')
        self.BT_NewUpdate.clicked.disconnect()
        self.PB_download.show()

        if not os.path.isdir(truePath('Updates')):
            os.mkdir(truePath('Updates'))

        save_path = truePath(f'Updates\\{self.new_version.split("/")[-1]}')
        urllib.request.urlretrieve(self.new_version, save_path, self.download_progress_bar_updater)

    def download_progress_bar_updater(self, blocknum, blocksize, totalsize):
        """ Updates the progress bar accordingly"""
        readed_data = blocknum * blocksize

        if totalsize > 0:
            download_percentage = readed_data * 100 / totalsize
            self.PB_download.setValue(int(download_percentage))
            QtWidgets.QApplication.processEvents()

            if download_percentage >= 100:
                self.update_is_ready_for_install()
                self.downloading = False

    def update_is_ready_for_install(self):
        """ Changes button text and connect it to another function"""
        self.BT_NewUpdate.setText('Restart and update')
        self.BT_NewUpdate.setEnabled(True)
        self.BT_NewUpdate.setStyleSheet('font-weight: bold; background-color: #5BD3C4')
        try:
            self.BT_NewUpdate.clicked.disconnect()
        except Exception:
            pass
        self.BT_NewUpdate.clicked.connect(self.install_update)

    def install_update(self):
        """ Starts the installation """
        archive = truePath(f'Updates\\{self.new_version.split("/")[-1]}')
        where_to_extract = truePath('Updates\\New')
        app_folder = truePath('')

        # Check if it's corrupt
        if HF.archive_is_corrupt(archive):
            os.remove(archive)
            self.sendInfoMessage('Archive corrupt. Removing file.', color=MColors.msg_failure)

            self.BT_NewUpdate.clicked.disconnect()
            self.BT_NewUpdate.clicked.connect(self.start_download)
            self.BT_NewUpdate.setText('Download update')
            return

        # Delete previously extracted archive
        if os.path.isdir(where_to_extract):
            shutil.rmtree(where_to_extract)

        # Extract archive
        HF.extract_archive(archive, where_to_extract)

        # Create and run install.bat file
        installfile = truePath('install.bat')
        with open(installfile, 'w') as f:
            f.write('\n'.join(('@echo off',
                                'echo Installation will start shortly...',
                                'timeout /t 7 /nobreak > NUL',
                                f'robocopy "{where_to_extract}" "{os.path.abspath(app_folder)}" /E',
                                'timeout /t 7 /nobreak > NUL',
                                f'rmdir /s /q "{truePath("Updates")}"',
                                'echo Installation completed...',
                                f'"{truePath("SCO.exe")}"'
                                ))) # yapf: disable

        self.saveSettings()
        os.startfile(installfile)
        app.quit()

    def updateUI(self):
        """ Update UI elements based on the current settings """
        self.TAB_Main.CH_StartWithWindows.setChecked(SM.settings['start_with_windows'])
        self.TAB_Main.CH_StartMinimized.setChecked(SM.settings['start_minimized'])
        self.TAB_Main.CH_EnableLogging.setChecked(SM.settings['enable_logging'])
        self.TAB_Main.CH_ShowPlayerWinrates.setChecked(SM.settings['show_player_winrates'])
        self.TAB_Main.CH_ForceHideOverlay.setChecked(SM.settings['force_hide_overlay'])
        self.TAB_Main.CH_DarkTheme.setChecked(SM.settings['dark_theme'])
        self.TAB_Main.CH_FastExpand.setChecked(SM.settings['fast_expand'])
        self.TAB_Main.CH_MinimizeToTray.setChecked(SM.settings['minimize_to_tray'])
        self.TAB_Main.CH_MinimizeToTray.stateChanged.connect(self.saveSettings)
        self.TAB_Main.SP_Duration.setProperty("value", SM.settings['duration'])
        self.TAB_Main.SP_Monitor.setProperty("value", SM.settings['monitor'])
        self.TAB_Main.LA_CurrentReplayFolder.setText(SM.settings['account_folder'])
        self.TAB_Main.LA_ScreenshotLocation.setText(SM.settings['screenshot_folder'])
        self.TAB_Main.CH_ShowSession.setChecked(SM.settings['show_session'])

        self.TAB_Main.KEY_ShowHide.setKeySequence(QtGui.QKeySequence.fromString(SM.settings['hotkey_show/hide']))
        self.TAB_Main.KEY_Show.setKeySequence(QtGui.QKeySequence.fromString(SM.settings['hotkey_show']))
        self.TAB_Main.KEY_Hide.setKeySequence(QtGui.QKeySequence.fromString(SM.settings['hotkey_hide']))
        self.TAB_Main.KEY_Newer.setKeySequence(QtGui.QKeySequence.fromString(SM.settings['hotkey_newer']))
        self.TAB_Main.KEY_Older.setKeySequence(QtGui.QKeySequence.fromString(SM.settings['hotkey_older']))
        self.TAB_Main.KEY_Winrates.setKeySequence(QtGui.QKeySequence.fromString(SM.settings['hotkey_winrates']))

        self.TAB_Main.ED_AomAccount.setText(SM.settings['aom_account'])
        self.TAB_Main.ED_AomSecretKey.setText(SM.settings['aom_secret_key'])

        self.TAB_Main.LA_P1.setText(f"Player 1 | {SM.settings['color_player1']}")
        self.TAB_Main.LA_P1.setStyleSheet(f"background-color: {SM.settings['color_player1']}; color: black")
        self.TAB_Main.LA_P2.setText(f"Player 2 | {SM.settings['color_player2']}")
        self.TAB_Main.LA_P2.setStyleSheet(f"background-color: {SM.settings['color_player2']}; color: black")
        self.TAB_Main.LA_Amon.setText(f"  Amon | {SM.settings['color_amon']}")
        self.TAB_Main.LA_Amon.setStyleSheet(f"background-color: {SM.settings['color_amon']}; color: black")
        self.TAB_Main.LA_Mastery.setText(f"Mastery | {SM.settings['color_mastery']}")
        self.TAB_Main.LA_Mastery.setStyleSheet(f"background-color: {SM.settings['color_mastery']}; color: black")

        self.TAB_Randomizer.FR_RNG_Overlay.setChecked(SM.settings['show_random_on_overlay'])

        self.TAB_TwitchBot.ch_twitch.setChecked(SM.settings['twitchbot']['auto_start'])
        self.TAB_TwitchBot.ch_twitch_chat.setChecked(SM.settings['show_chat'])
        self.TAB_TwitchBot.ED_twitch_channel_name.setText(SM.settings['twitchbot']['channel_name'])

        self.TAB_Resources.ch_performance_show.setChecked(SM.settings['performance_show'])
        self.TAB_Resources.KEY_Performance.setKeySequence(QtGui.QKeySequence.fromString(SM.settings['performance_hotkey']))

        self.TAB_Stats.CH_FA_atstart.setChecked(SM.settings['full_analysis_atstart'])

        if SM.settings['debug_button']:
            self.DebugWindow = DebugWindow(self)

        # RNG choices
        self.TAB_Randomizer.load_choices(SM.settings['rng_choices'])

    def saveSettings(self):
        """ Saves main settings in the settings file. """
        previous_settings = SM.settings.copy()

        self.save_playernotes_to_settings()

        SM.settings['start_with_windows'] = self.TAB_Main.CH_StartWithWindows.isChecked()
        SM.settings['start_minimized'] = self.TAB_Main.CH_StartMinimized.isChecked()
        SM.settings['enable_logging'] = self.TAB_Main.CH_EnableLogging.isChecked()
        SM.settings['show_player_winrates'] = self.TAB_Main.CH_ShowPlayerWinrates.isChecked()
        SM.settings['force_hide_overlay'] = self.TAB_Main.CH_ForceHideOverlay.isChecked()
        SM.settings['dark_theme'] = self.TAB_Main.CH_DarkTheme.isChecked()
        SM.settings['fast_expand'] = self.TAB_Main.CH_FastExpand.isChecked()
        SM.settings['minimize_to_tray'] = self.TAB_Main.CH_MinimizeToTray.isChecked()
        SM.settings['show_session'] = self.TAB_Main.CH_ShowSession.isChecked()
        SM.settings['duration'] = self.TAB_Main.SP_Duration.value()
        SM.settings['monitor'] = self.TAB_Main.SP_Monitor.value()

        SM.settings['hotkey_show/hide'] = self.TAB_Main.KEY_ShowHide.keySequence().toString()
        SM.settings['hotkey_show'] = self.TAB_Main.KEY_Show.keySequence().toString()
        SM.settings['hotkey_hide'] = self.TAB_Main.KEY_Hide.keySequence().toString()
        SM.settings['hotkey_newer'] = self.TAB_Main.KEY_Newer.keySequence().toString()
        SM.settings['hotkey_older'] = self.TAB_Main.KEY_Older.keySequence().toString()
        SM.settings['hotkey_winrates'] = self.TAB_Main.KEY_Winrates.keySequence().toString()

        SM.settings['aom_account'] = self.TAB_Main.ED_AomAccount.text()
        SM.settings['aom_secret_key'] = self.TAB_Main.ED_AomSecretKey.text()
        SM.settings['twitchbot']['auto_start'] = self.TAB_TwitchBot.ch_twitch.isChecked()
        SM.settings['twitchbot']['channel_name'] = self.TAB_TwitchBot.ED_twitch_channel_name.text()

        SM.settings['full_analysis_atstart'] = self.TAB_Stats.CH_FA_atstart.isChecked()
        SM.settings['show_random_on_overlay'] = self.TAB_Randomizer.FR_RNG_Overlay.isChecked()

        SM.settings['show_chat'] = self.TAB_TwitchBot.ch_twitch_chat.isChecked()
        if hasattr(self, 'chat_widget'):
            SM.settings['chat_geometry'] = [
                self.chat_widget.pos().x(),
                self.chat_widget.pos().y(),
                self.chat_widget.width(), self.chat_widget.height()
            ]

        SM.settings['performance_show'] = self.TAB_Resources.ch_performance_show.isChecked()
        SM.settings['performance_hotkey'] = self.TAB_Resources.KEY_Performance.keySequence().toString()
        if hasattr(self, 'performance_overlay'):
            SM.settings['performance_geometry'] = [
                self.performance_overlay.pos().x(),
                self.performance_overlay.pos().y(),
                self.performance_overlay.width(),
                self.performance_overlay.height()
            ]

        # RNG choices
        SM.settings['rng_choices'] = self.TAB_Randomizer.get_choices()

        # Save settings
        SM.save_settings()

        # Message
        self.sendInfoMessage('Settings applied')

        # Check for overlapping hoykeys
        hotkeys = [
            SM.settings['performance_hotkey'], SM.settings['hotkey_show/hide'], SM.settings['hotkey_show'], SM.settings['hotkey_hide'],
            SM.settings['hotkey_newer'], SM.settings['hotkey_older'], SM.settings['hotkey_winrates']
        ]

        hotkeys = [h for h in hotkeys if not h in {None, ''}]
        if len(hotkeys) > len(set(hotkeys)):
            self.sendInfoMessage('Warning: Overlapping hotkeys!', color=MColors.msg_failure)

        # Registry
        out = HF.add_to_startup(SM.settings['start_with_windows'])
        if out is not None:
            self.sendInfoMessage(f'Warning: {out}', color=MColors.msg_failure)
            SM.settings['start_with_windows'] = False
            self.TAB_Main.CH_StartWithWindows.setChecked(SM.settings['start_with_windows'])

        # Logging
        logclass.LOGGING = SM.settings['enable_logging'] if self.write_permissions else False

        # Update settings for other threads
        MF.update_init_message()

        # Compare
        changed_keys = set()
        for key in previous_settings:
            if previous_settings[key] != SM.settings[key] and not (previous_settings[key] is None and SM.settings[key] == ''):
                if key == 'aom_secret_key':
                    logger.info(f'Changed: {key}: ... → ...')
                else:
                    logger.info(f'Changed: {key}: {previous_settings[key]} → {SM.settings[key]}')
                changed_keys.add(key)

        # Resend init message if duration has changed. Colors are handle in color picker.
        if 'duration' in changed_keys:
            MF.resend_init_message()

        # Monitor update
        if 'monitor' in changed_keys and hasattr(self, 'WebView'):
            self.set_WebView_size_location(SM.settings['monitor'])

        # Update keyboard threads
        self.manage_keyboard_threads(previous_settings=previous_settings)

        # Show/hide overlay
        if hasattr(self, 'WebView') and SM.settings['force_hide_overlay'] and self.WebView.isVisible():
            self.WebView.hide()
        elif hasattr(self, 'WebView') and not SM.settings['force_hide_overlay'] and not self.WebView.isVisible():
            self.WebView.show()

    def hotkey_changed(self):
        """ Wait a bit for the sequence to update, and then check if not to delete the key"""
        self.hotkey_changed_timer = QtCore.QTimer()
        self.hotkey_changed_timer.setInterval(50)
        self.hotkey_changed_timer.setSingleShot(True)
        self.hotkey_changed_timer.timeout.connect(self.check_to_remove_hotkeys)
        self.hotkey_changed_timer.start()

    def check_to_remove_hotkeys(self):
        """ Checks if a key is 'Del' and sets it to None """
        key_dict = {
            self.TAB_Main.KEY_ShowHide: 'hotkey_show/hide',
            self.TAB_Main.KEY_Show: 'hotkey_show',
            self.TAB_Main.KEY_Hide: 'hotkey_hide',
            self.TAB_Main.KEY_Newer: 'hotkey_newer',
            self.TAB_Main.KEY_Older: 'hotkey_older',
            self.TAB_Main.KEY_Winrates: 'hotkey_winrates',
            self.TAB_Resources.KEY_Performance: 'performance_hotkey'
        }

        for key in key_dict:
            if key.keySequence().toString() == 'Del':
                key.setKeySequence(QtGui.QKeySequence.fromString(None))
                logger.info(f"Removed key for {key_dict[key]}")
                self.saveSettings()
                break

    def manage_keyboard_threads(self, previous_settings=None):
        """ Compares previous settings with current ones, and restarts keyboard threads if necessary.
        if `previous_settings` == None, then init hotkeys instead """
        hotkey_func_dict = {
            'performance_hotkey': self.signal_manager.showHidePerfOverlay.emit,
            'hotkey_show/hide': MF.keyboard_SHOWHIDE,
            'hotkey_show': MF.keyboard_SHOW,
            'hotkey_hide': MF.keyboard_HIDE,
            'hotkey_newer': MF.keyboard_NEWER,
            'hotkey_older': MF.keyboard_OLDER,
            'hotkey_winrates': MF.keyboard_PLAYERWINRATES
        }

        # Init
        if previous_settings is None:
            self.hotkey_hotkey_dict = dict()
            for key in hotkey_func_dict:
                if not SM.settings[key] in {None, ''}:
                    try:
                        self.hotkey_hotkey_dict[key] = keyboard.add_hotkey(SM.settings[key], hotkey_func_dict[key])
                    except Exception:
                        logger.error(traceback.format_exc())
                        self.sendInfoMessage(f'Failed to initialize hotkey ({key.replace("hotkey_","")})! Try a different one.',
                                             color=MColors.msg_failure)
        # Update
        else:
            for key in hotkey_func_dict:
                # Update current value if the hotkey changed
                if previous_settings[key] != SM.settings[key] and not SM.settings[key] in {None, ''}:
                    if key in self.hotkey_hotkey_dict:
                        keyboard.remove_hotkey(self.hotkey_hotkey_dict[key])
                    try:
                        self.hotkey_hotkey_dict[key] = keyboard.add_hotkey(SM.settings[key], hotkey_func_dict[key])
                        logger.info(f'Changed hotkey of {key} to {SM.settings[key]}')
                    except Exception:
                        logger.error(f'Failed to change hotkey {key}\n{traceback.format_exc()}')

                # Remove current hotkey no value
                elif SM.settings[key] in {None, ''} and key in self.hotkey_hotkey_dict:
                    try:
                        keyboard.remove_hotkey(self.hotkey_hotkey_dict[key])
                        del self.hotkey_hotkey_dict[key]
                        logger.info(f'Removing hotkey of {key}')
                    except Exception:
                        logger.error(f'Failed to remove hotkey {key}\n{traceback.format_exc()}')

    def resetSettings(self):
        """ Resets settings to default values and updates UI """
        previous_settings = SM.settings.copy()
        SM.settings = SM.default_settings.copy()
        SM.settings['account_folder'] = HF.get_account_dir(path=SM.settings['account_folder'])
        SM.settings['screenshot_folder'] = previous_settings['screenshot_folder']
        SM.settings['aom_account'] = self.TAB_Main.ED_AomAccount.text()
        SM.settings['aom_secret_key'] = self.TAB_Main.ED_AomSecretKey.text()
        SM.settings['player_notes'] = previous_settings['player_notes']
        SM.settings['twitchbot'] = previous_settings['twitchbot']
        SM.settings['debug_button'] = previous_settings['debug_button']
        SM.settings['debug'] = previous_settings['debug']
        self.updateUI()
        self.saveSettings()
        self.sendInfoMessage('All settings have been reset!')
        MF.update_init_message()
        MF.resend_init_message()
        self.manage_keyboard_threads(previous_settings=previous_settings)

    def chooseScreenshotFolder(self):
        """ Changes screenshot folder location """
        dialog = QtWidgets.QFileDialog()
        dialog.setDirectory(SM.settings['screenshot_folder'])
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        if dialog.exec_():
            folder = os.path.normpath(dialog.selectedFiles()[0])
            logger.info(f'Changing screenshot_folder to {folder}')
            self.TAB_Main.LA_ScreenshotLocation.setText(folder)
            SM.settings['screenshot_folder'] = folder
            self.sendInfoMessage(f'Screenshot folder set succesfully! ({folder})', color=MColors.msg_success)

    def findReplayFolder(self):
        """ Finds and sets account folder """
        dialog = QtWidgets.QFileDialog()
        if not SM.settings['account_folder'] in {None, ''}:
            dialog.setDirectory(SM.settings['account_folder'])
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        if dialog.exec_():
            folder = dialog.selectedFiles()[0]
            if 'StarCraft' in folder and '/Accounts' in folder:
                logger.info(f'Changing accountdir to {folder}')
                SM.settings['account_folder'] = folder
                self.TAB_Main.LA_CurrentReplayFolder.setText(folder)
                self.sendInfoMessage(f'Account folder set succesfully! ({folder})', color=MColors.msg_success)
                MF.update_names_and_handles(folder, MF.AllReplays)
                if hasattr(self, 'CAnalysis'):
                    self.updating_maps = QtWidgets.QWidget()
                    self.updating_maps.setWindowTitle('Adding replays')
                    self.updating_maps.setGeometry(700, 500, 300, 100)
                    self.updating_maps.setWindowIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
                    self.updating_maps_label = QtWidgets.QLabel(self.updating_maps)
                    self.updating_maps_label.setGeometry(QtCore.QRect(10, 10, 280, 80))
                    self.updating_maps_label.setText('<b>Please wait</b><br><br>You might need to restart for the game list and stats to update.')
                    self.updating_maps_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    self.updating_maps_label.setWordWrap(True)
                    self.updating_maps.show()
                    self.CAnalysis.update_accountdir(folder)
                    self.updating_maps.hide()
                    self.TAB_Stats.generate_stats()
                    self.update_winrate_data()

            else:
                self.sendInfoMessage('Invalid account folder!', color=MColors.msg_failure)

    def start_main_functionality(self):
        """ Doing the main work of looking for replays, analysing, etc. """
        logger.info(f'\n>>> Starting ({APPVERSION/100:.2f})!\n{SM.settings_for_logs()}')

        # Get monitor dimensions
        self.desktop_widget = QtWidgets.QDesktopWidget()
        self.sg = self.desktop_widget.screenGeometry(int(SM.settings['monitor'] - 1))

        # Debug files in MEI directory
        if SM.settings['debug']:
            folder = os.path.abspath(innerPath(''))
            if os.path.isdir(folder):
                for root, _, files in os.walk(folder):
                    for file in files:
                        logger.info(f'>>File: {os.path.abspath(os.path.join(root, file))}')
            else:
                logger.error(f"No dir: {folder}")

        # Custom CSS/JS
        if not os.path.isfile(truePath('Layouts/custom.css')):
            with open(truePath('Layouts/custom.css'), 'w') as f:
                f.write('/* insert custom css here */')

        if not os.path.isfile(truePath('Layouts/custom.js')):
            with open(truePath('Layouts/custom.js'), 'w') as f:
                f.write('// insert custom javascript here')

        # Load overlay
        if not os.path.isfile(truePath('Layouts/Layout.html')):
            self.sendInfoMessage("Error! Failed to locate the html file", color=MColors.msg_failure)
            logger.error("Error! Failed to locate the html file")

        else:
            self.WebView = MUI.CustomWebView()
            self.WebView.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowTransparentForInput | QtCore.Qt.WindowStaysOnTopHint
                                        | eval(f"QtCore.Qt.{SM.settings['webflag']}") | QtCore.Qt.NoDropShadowWindowHint
                                        | QtCore.Qt.WindowDoesNotAcceptFocus)

            self.WebView.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

            self.WebPage = self.WebView.page()
            self.WebPage.setBackgroundColor(QtCore.Qt.transparent)
            self.set_WebView_size_location(SM.settings['monitor'])

            self.WebView.load(QtCore.QUrl().fromLocalFile(truePath('Layouts/Layout.html')))

            if not SM.settings['force_hide_overlay']:
                self.WebView.show()

            MF.WEBPAGE = self.WebPage

        # Pass current settings
        MF.update_init_message()

        # Init randomization
        self.TAB_Randomizer.randomize_commander()

        # Start server thread
        self.thread_server = threading.Thread(target=MF.server_thread, daemon=True)
        self.thread_server.start()

        # Init replays, names & handles. This should be fast
        MF.initialize_replays_names_handles()

        # PyQt threadpool
        self.threadpool = QtCore.QThreadPool()

        # Check for new replays
        thread_replays = MUI.Worker(MF.check_replays)
        thread_replays.signals.result.connect(self.check_replays_finished)
        self.threadpool.start(thread_replays)

        # Start mass replay analysis
        thread_mass_analysis = MUI.Worker(MR.mass_replay_analysis_thread, SM.settings['account_folder'])
        thread_mass_analysis.signals.result.connect(self.mass_analysis_finished)
        self.threadpool.start(thread_mass_analysis)
        logger.info('Starting mass replay analysis')

        # Check for the PC to be awoken from sleep
        thread_awakening = MUI.Worker(MF.wait_for_wake)
        thread_awakening.signals.result.connect(self.pc_waken_from_sleep)
        self.threadpool.start(thread_awakening)

        # Create chat widget
        if SM.settings['show_chat']:
            self.create_twitch_chat()

        # Create the twitch bot
        if SM.settings['twitchbot']['auto_start']:
            self.run_twitch_bot()

        # Performance overlay
        self.performance_overlay = SystemInfo(geometry=SM.settings['performance_geometry'], process_names=SM.settings['performance_processes'])
        if SM.settings['performance_show']:
            self.TAB_Resources.ch_performance_show.setChecked(True)
            self.performance_overlay.start()

        # Find MM Integration banks
        self.TAB_TwitchBot.find_and_update_banks()
        self.update_selected_bank_item(SM.settings['twitchbot']['bank_locations'].get('Current'))

    def change_bank(self):
        """ Update currently used bank in the twitch bot.
        Used when user changes combo-box directly"""
        bank_path = self.bank_name_to_location_dict.get(self.TAB_TwitchBot.CB_twitch_banks.currentText(),
                                                        self.TAB_TwitchBot.CB_twitch_banks.currentText())
        logger.info(f'Changing bank to {bank_path}')
        SM.settings['twitchbot']['bank_locations']['Current'] = bank_path
        try:
            self.TwitchBot.bank = bank_path
        except Exception:
            logger.info('Failed to set bank for twitch bot')

    def update_selected_bank_item(self, bank_path):
        """ Updates selected bank indirectly (when user didn't click it directly)"""
        if bank_path in {'', None}:
            logger.error('Not valid bank path, not changing')
            return

        logger.info(f'Changing bank indirectly to {bank_path.strip()}')

        for i in range(self.TAB_TwitchBot.CB_twitch_banks.count()):
            if bank_path in self.TAB_TwitchBot.CB_twitch_banks.itemText(i):
                SM.settings['twitchbot']['bank_locations']['Current'] = bank_path
                self.TAB_TwitchBot.CB_twitch_banks.setCurrentIndex(i)
                try:
                    self.TwitchBot.bank = bank_path
                except Exception:
                    logger.info('Failed to set bank for twitch bot')
                break

        logger.info('Bank changed indirectly succesfully')

    def run_twitch_bot(self):
        """Runs the twitch bot. But first checks if bot name and oauth are set. If not, tries to fallback on my bot settings. """
        twitchbot_settings = SM.settings['twitchbot'].copy()

        # Fallback to my bot if the user doesn't have its own bot
        if SM.settings['twitchbot']['channel_name'] != '' and SM.settings['twitchbot']['bot_name'] == '' and SM.settings['twitchbot'][
                'bot_oauth'] == '':
            file = innerPath('src/secure.json')
            if os.path.isfile(file):
                with open(file, 'r') as f:
                    fallback = json.load(f)

                logger.info('Falling back on my twitch bot settings')
                twitchbot_settings['bot_name'] = fallback['bot_name']
                twitchbot_settings['bot_oauth'] = fallback['bot_oauth']

        # Run the both if settings are ok
        if twitchbot_settings['channel_name'] == '' or twitchbot_settings['bot_name'] == '' or twitchbot_settings['bot_oauth'] == '':
            logger.error(
                f"Invalid data for the bot\n{SM.settings['twitchbot']['channel_name']=}\n{SM.settings['twitchbot']['bot_name']=}\n{SM.settings['twitchbot']['bot_oauth']=}"
            )
            self.TAB_TwitchBot.LA_InfoTwitch.setText('Twitch bot not started. Check your settings!')
        else:
            self.TwitchBot = TwitchBot(twitchbot_settings, widget=self.chat_widget if hasattr(self, 'chat_widget') else None)
            self.thread_twitch_bot = threading.Thread(target=self.TwitchBot.run_bot, daemon=True)
            self.thread_twitch_bot.start()
            self.TAB_TwitchBot.bt_twitch.setText('Stop the bot')

    def set_WebView_size_location(self, monitor):
        """ Set correct size and width for the widget. Setting it to full shows black screen on my machine, works fine on notebook (thus -1 offset) """
        try:
            self.WebView.setFixedSize(int(self.sg.width() * SM.settings['width']),
                                      int(self.sg.height() * SM.settings['height']) - SM.settings['subtract_height'])

            # Calculate correct X offset when considering multiple monitors. Sum all widths including the current monitor.
            x_start = 0
            for i in range(0, SM.settings['monitor']):
                x_start += self.desktop_widget.screenGeometry(i).width()
            # Substract widget  width and offset
            x = x_start - self.sg.width() * SM.settings['width'] + SM.settings['right_offset']
            # Move widget
            self.WebView.move(int(x), self.sg.top())
            logger.info(f'Using monitor {int(monitor)} ({self.sg.width()}x{self.sg.height()})')
        except Exception:
            logger.error(f"Failed to set to monitor {monitor}\n{traceback.format_exc()}")

    def pc_waken_from_sleep(self, diff):
        """ This function is run when the PC is awoken """
        if diff is None:
            return
        logger.info(f'The computer just awoke! ({diff:.0f} seconds)')
        thread_awakening = MUI.Worker(MF.wait_for_wake)
        thread_awakening.signals.result.connect(self.pc_waken_from_sleep)
        self.threadpool.start(thread_awakening)
        self.reset_keyboard_thread()

    def reset_keyboard_thread(self):
        """ Resets keyboard thread"""
        try:
            keyboard.unhook_all()
            keyboard._listener = keyboard._KeyboardListener()
            keyboard._listener.start_if_necessary()
            self.manage_keyboard_threads()
            logger.info(f'Reseting keyboard thread')
        except Exception:
            logger.error(f"Failed to reset keyboard\n{traceback.format_exc}")

    def check_replays_finished(self, replay_dict):
        """ Launches function again. Adds game to game tab. Updates player winrate data. """

        # Show/hide overlay (just to make sure)
        if hasattr(self, 'WebView') and SM.settings['force_hide_overlay'] and self.WebView.isVisible():
            self.WebView.hide()
        elif hasattr(self, 'WebView') and not SM.settings['force_hide_overlay']:
            self.WebView.show()

        # Launch thread anew
        thread_replays = MUI.Worker(MF.check_replays)
        thread_replays.signals.result.connect(self.check_replays_finished)
        self.threadpool.start(thread_replays)

        # Delay updating new data to prevent lag when showing the overlay
        self.timeoutTimer = QtCore.QTimer()
        self.timeoutTimer.setInterval(2000)
        self.timeoutTimer.setSingleShot(True)
        self.timeoutTimer.timeout.connect(partial(self.TAB_Games.add_new_game_data, replay_dict))
        self.timeoutTimer.start()

    def save_playernotes_to_settings(self):
        """ Saves player notes from UI to settings dict"""
        for player in self.TAB_Players.player_winrate_UI_dict:
            if not self.TAB_Players.player_winrate_UI_dict[player].get_note() in {None, ''}:
                SM.settings['player_notes'][player] = self.TAB_Players.player_winrate_UI_dict[player].get_note()
            elif player in SM.settings['player_notes']:
                del SM.settings['player_notes'][player]

    def wait_ms(self, time):
        """ Pause executing for `time` in miliseconds"""
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(time, loop.quit)
        loop.exec_()

    @catch_exceptions(logger)
    def mass_analysis_finished(self, result):
        self.CAnalysis = result

        # Update game tab
        self.TAB_Games.initialize_data(self.CAnalysis)

        # Update stats tab
        player_names = (', ').join(self.CAnalysis.main_names)
        self.TAB_Stats.LA_IdentifiedPlayers.setText(f"Main players: {player_names}")
        self.TAB_Stats.LA_GamesFound.setText(f"Games found: {len(self.CAnalysis.ReplayData)}")
        self.TAB_Stats.LA_Stats_Wait.deleteLater()
        self.TAB_Games.LA_Games_Wait.deleteLater()
        self.TAB_Stats.generate_stats()

        self.update_winrate_data()
        MF.check_names_handles()
        MF.CAnalysis = self.CAnalysis

        # Show player winrates
        if SM.settings['show_player_winrates']:
            thread_check_for_newgame = MUI.Worker(MF.check_for_new_game, progress_callback=True)
            thread_check_for_newgame.signals.progress.connect(self.map_identified)
            self.threadpool.start(thread_check_for_newgame)

        # Connect & run full analysis if set
        self.TAB_Stats.BT_FA_run.setEnabled(True)
        self.TAB_Stats.BT_FA_run.clicked.connect(self.run_f_analysis)
        if SM.settings['full_analysis_atstart']:
            self.run_f_analysis()

        # If try to find
        self.find_default_bank_location()

        # Change bank names
        self.bank_name_to_location_dict = self.TAB_TwitchBot.change_bank_names(self.CAnalysis)

        # Enable selecting banks
        self.TAB_TwitchBot.CB_twitch_banks.currentIndexChanged.connect(self.change_bank)
        self.TAB_TwitchBot.CB_twitch_banks.setEnabled(True)

        # Dump & reinit
        self.TAB_Stats.BT_FA_dump.setEnabled(True)
        self.TAB_Stats.BT_FA_dump.clicked.connect(self.dump_all)

    def map_identified(self, data):
        """Shows fast expand widget when a valid new map is identified"""
        logger.info(f'Identified map: {data}')

        # Don't proceed if the function disabled or not a valid map
        if not SM.settings['fast_expand'] or not data[0] in FastExpandSelector.valid_maps:
            return

        if self.FastExpandSelector is None:
            self.FastExpandSelector = FastExpandSelector()
        self.FastExpandSelector.setData(data)
        self.FastExpandSelector.show()

    def dump_all(self):
        """ Dumps all replay data from mass analysis into a file """
        self.TAB_Stats.BT_FA_dump.setEnabled(False)
        thread_dump_all = MUI.Worker(self.CAnalysis.dump_all)
        thread_dump_all.signals.result.connect(partial(self.TAB_Stats.BT_FA_dump.setEnabled, True))
        self.threadpool.start(thread_dump_all)

    def run_f_analysis(self):
        """ runs full analysis """
        if self.full_analysis_running:
            logger.error('Full analysis is already running')
            return

        self.TAB_Stats.BT_FA_run.setEnabled(False)
        self.TAB_Stats.BT_FA_stop.setEnabled(True)
        self.full_analysis_running = True
        thread_full_analysis = MUI.Worker(self.CAnalysis.run_full_analysis, progress_callback=True)
        thread_full_analysis.signals.result.connect(self.full_analysis_finished)
        thread_full_analysis.signals.progress.connect(self.full_analysis_progress)
        self.threadpool.start(thread_full_analysis)

    def full_analysis_progress(self, progress):
        """ Updates progress from full analysis"""
        self.TAB_Stats.CH_FA_status.setText(progress)

    def full_analysis_finished(self, finished_completely):
        self.TAB_Stats.generate_stats()
        if finished_completely:
            self.TAB_Stats.CH_FA_atstart.setChecked(True)

    def stop_full_analysis(self):
        if hasattr(self, 'CAnalysis'):
            self.CAnalysis.closing = True
            self.full_analysis_running = False
            self.TAB_Stats.BT_FA_run.setEnabled(True)
            self.TAB_Stats.BT_FA_stop.setEnabled(False)
            self.CAnalysis.save_cache()

    def update_winrate_data(self):
        """ Update player tab & set winrate data in MF """
        if hasattr(self, 'CAnalysis'):
            self.winrate_data = self.CAnalysis.calculate_player_winrate_data()
            self.TAB_Players.update(self.winrate_data)
            MF.set_player_winrate_data(self.winrate_data)
        else:
            logger.error('Can\'t update winrate data before mass analysis is finished')

    def save_screenshot(self):
        """ Saves screenshot of the overlay and saves it on the desktop"""
        try:
            p = QtGui.QImage(self.WebView.grab())
            height = p.height() * 1060 / 1200
            width = p.height() * 650 / 1200
            p = p.copy(int(p.width() - width), int(p.height() * 20 / 1200), int(width), int(height))
            p = p.convertToFormat(QtGui.QImage.Format_RGB888)

            name = f'Overlay_{datetime.now().strftime("%H%M%S")}.png'
            path = os.path.abspath(os.path.join(SM.settings['screenshot_folder'], name))

            p.save(path, 'png')

            # Files smaller than 10kb consider as empty
            if os.path.getsize(path) < 10000:
                self.sendInfoMessage(f'Show overlay before taking screenshot!', color=MColors.msg_failure)
                os.remove(path)
            else:
                logger.info(f'Taking screenshot! {path}')
                self.sendInfoMessage(f'Taking screenshot! {path}', color=MColors.msg_success)
        except Exception:
            logger.error(traceback.format_exc())

    def start_stop_bot(self):
        """ Starts or stops the twitch bot """
        SM.settings['twitchbot']['channel_name'] = self.TAB_TwitchBot.ED_twitch_channel_name.text()

        if hasattr(self, 'TwitchBot'):
            if self.TwitchBot.RUNNING:
                self.TwitchBot.RUNNING = False
                self.TAB_TwitchBot.bt_twitch.setText('Run the bot')
            else:
                self.TwitchBot.RUNNING = True
                self.TAB_TwitchBot.bt_twitch.setText('Stop the bot')
        else:
            self.run_twitch_bot()

    def update_twitch_chat_position(self):
        """ Updates state of the chat widget. Whether it can be moved or not."""
        if not hasattr(self, 'chat_widget'):
            return

        position = self.chat_widget.pos()

        if self.chat_widget.fixed:
            self.chat_widget.fixed = False
            self.chat_widget.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
            self.chat_widget.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
            self.chat_widget.move(position.x() - 8, position.y() - 31)
            self.chat_widget.show()
            self.TAB_TwitchBot.bt_twitch_position.setText('Fix chat position')
        else:
            self.chat_widget.fixed = True
            self.chat_widget.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowTransparentForInput | QtCore.Qt.WindowStaysOnTopHint
                                            | QtCore.Qt.CoverWindow | QtCore.Qt.NoDropShadowWindowHint | QtCore.Qt.WindowDoesNotAcceptFocus)

            self.chat_widget.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
            self.chat_widget.move(position.x() + 8, position.y() + 31)
            self.chat_widget.show()
            self.TAB_TwitchBot.bt_twitch_position.setText('Change chat position')

    def create_twitch_chat(self):
        """ Creates or updates twitch chat"""

        # Hide
        if hasattr(self, 'chat_widget') and not self.TAB_TwitchBot.ch_twitch_chat.isChecked():
            self.chat_widget.hide()

        # Show
        elif hasattr(self, 'chat_widget') and self.TAB_TwitchBot.ch_twitch_chat.isChecked():
            self.chat_widget.show()

        # Creates twitch chat widget if it's not created already
        elif not hasattr(self, 'chat_widget'):
            self.chat_widget = ChatWidget(geometry=SM.settings['chat_geometry'], chat_font_scale=SM.settings['chat_font_scale'])

            if hasattr(self, 'TwitchBot'):
                self.TwitchBot.widget = self.chat_widget

    def update_performance_overlay_position(self):
        """ Updates state of the performance overlay widget. Whether it can be moved or not."""
        if not hasattr(self, 'performance_overlay'):
            return

        if not self.performance_overlay.started:
            return

        position = self.performance_overlay.pos()

        if self.performance_overlay.fixed:
            self.performance_overlay.fixed = False
            self.performance_overlay.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
            self.performance_overlay.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
            self.performance_overlay.show()
            self.performance_overlay.move(position.x() - 8, position.y() - 31)
            self.TAB_Resources.bt_performance_overlay_position.setText('Fix overlay position')
        else:
            self.performance_overlay.fixed = True
            self.performance_overlay.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowTransparentForInput
                                                    | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.CoverWindow | QtCore.Qt.NoDropShadowWindowHint
                                                    | QtCore.Qt.WindowDoesNotAcceptFocus)
            self.performance_overlay.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
            self.performance_overlay.show()
            self.performance_overlay.move(position)
            self.TAB_Resources.bt_performance_overlay_position.setText('Change overlay position')

    def show_hide_performance_overlay(self):
        """ Shows/hides peformance overlay. Triggered by hotkey """
        if not hasattr(self, 'performance_overlay'):
            return

        if self.performance_overlay.isVisible():
            self.performance_overlay.hide()
            self.TAB_Resources.ch_performance_show.setChecked(False)
        else:
            self.performance_overlay.show()
            self.TAB_Resources.ch_performance_show.setChecked(True)
            if not self.performance_overlay.started:
                self.performance_overlay.start()

    def find_default_bank_location(self):
        """ Finds default bank location (Runs after mass analysis is finished)"""

        try:
            result = self.CAnalysis.find_banks()
            result = list(result.values())[0][1]
            result = os.path.join(result, 'MMTwitchIntegration.SC2Bank')
            SM.settings['twitchbot']['bank_locations']['Default'] = result
            logger.info(f"Setting default bank location to {result.strip()}")
            self.update_selected_bank_item(result)
        except IndexError:
            logger.error('Didnt find bank locations')
        except Exception:
            logger.error(traceback.format_exc())

    def sendInfoMessage(self, message, color=None):
        """ Sends info message. `color` specifies message color"""
        self.TAB_Main.LA_InfoLabel.setText(message)
        self.TAB_Main.LA_InfoLabel.setStyleSheet(f'color: {color if color is not None else MColors.msg}')

    def change_theme(self):
        """ Changes theme to dark or asks for restart"""
        if self.TAB_Main.CH_DarkTheme.isChecked():
            set_dark_theme(self, app, TabWidget, APPVERSION)
        else:
            self.sendInfoMessage('Restart to change back to the light theme!', color=MColors.msg_failure)


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    TabWidget = MUI.CustomQTabWidget()
    try:
        ui = UI_TabWidget()
        ui.setupUI(TabWidget)
        ui.loadSettings()
        ui.start_main_functionality()
    except MultipleInstancesRunning:
        sys.exit()
    except Exception:
        logger.error(traceback.format_exc())
        TabWidget.tray_icon.hide()
        MF.stop_threads()
        sys.exit()

    # Do stuff before the app is closed
    exit_event = app.exec_()
    TabWidget.tray_icon.hide()
    ui.stop_full_analysis()
    MF.stop_threads()
    ui.saveSettings()
    sys.exit(exit_event)