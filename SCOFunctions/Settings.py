import os
import json
import traceback
from datetime import datetime

from SCOFunctions.MLogging import logclass
logger = logclass('SETT', 'INFO')


def update_with_defaults(loaded: dict, default: dict):
    """ Checks `loaded` dictionary, and fills all keys that are not present with values
    from `default` dictionary. This is done recursively for any dictionaries inside"""
    if not isinstance(default, dict) or not isinstance(loaded, dict):
        raise TypeError('default and loaded has to be dictionaries')

    for key in default:
        # If there is a new key
        if not key in loaded:
            loaded[key] = default[key]
        # If dictionary recursively do the same
        if isinstance(default[key], dict):
            update_with_defaults(loaded[key], default[key])


class CSettings:
    def __init__(self):
        self.filepath = None
        self.default_settings = {
            'start_with_windows': False,
            'start_minimized': False,
            'enable_logging': True,
            'show_player_winrates': True,
            'duration': 60,
            'monitor': 1,
            'force_hide_overlay': False,
            'show_session': True,
            'show_random_on_overlay': False,
            'dark_theme': True,
            'fast_expand': False, 
            'minimize_to_tray': True,
            'account_folder': None,
            'screenshot_folder': None,
            'hotkey_show/hide': 'Ctrl+Shift+*',
            'hotkey_show': None,
            'hotkey_hide': None,
            'hotkey_newer': 'Ctrl+Alt+/',
            'hotkey_older': 'Ctrl+Alt+*',
            'hotkey_winrates': 'Ctrl+Alt+-',
            'color_player1': '#0080F8',
            'color_player2': '#00D532',
            'color_amon': '#FF0000',
            'color_mastery': '#FFDC87',
            'aom_account': None,
            'aom_secret_key': None,
            'player_notes': dict(),
            'main_names': list(),
            'list_games': 100,
            'right_offset': 0,
            'top_offset': 0,
            'width': 0.7,
            'show_charts': True,
            'replay_check_interval': 3,
            'height': 1,
            'font_scale': 1,
            'check_for_multiple_instances': True,
            'subtract_height': 1,
            'rng_choices': dict(),
            'performance_geometry': None,
            'performance_show': False,
            'performance_hotkey': None,
            'performance_processes': ['SC2_x64.exe', 'SC2.exe'],
            'show_chat': False,
            'chat_geometry': (700, 300, 500, 500),
            'chat_font_scale': 1.3,
            'webflag': 'CoverWindow',
            'full_analysis_atstart': False,
            'twitchbot': {
                'channel_name': '',
                'bot_name': '',
                'bot_oauth': '',
                'bank_locations': {
                    'Default': '',
                    'Current': ''
                },
                'responses': {
                    'commands': '!names, !syntax, !overlay, !join, !message, !mutator, !spawn, !wave, !resources',
                    'syntax':
                    '!spawn unit_type amount for_player (e.g. !spawn marine 10 2), !wave size tech (e.g. !wave 7 7), !resources minerals vespene for_player \
                                                            (e.g. !resources 1000 500 2), !mutator mutator_name (e.g. !mutator avenger), !mutator mutator_name disable, !join player (e.g. !join 2).',
                    'overlay': 'https://github.com/FluffyMaguro/SC2_Coop_overlay',
                    'maguro': 'www.maguro.one',
                    'names': 'https://www.maguro.one/p/unit-names.html'
                },
                'greetings': {
                    'fluffymaguro': 'Hello Maguro!'
                },
                'banned_mutators': ['Vertigo', 'Propagators', 'Fatal Attraction'],
                'banned_units': [
                    '',
                ],
                'host': 'irc.twitch.tv',
                'port': 6667,
                'auto_start': False,
            }
        }

        # We don't need a deepcopy here. When resetting only the lower level gets changed.
        self.settings = self.default_settings.copy()

    def load_settings(self, filepath):
        """ Load settings from a file"""
        self.filepath = filepath
        try:
            # Try to load base config if there is one
            if os.path.isfile(self.filepath):
                with open(self.filepath, 'r') as f:
                    self.settings = json.load(f)

            # If it's not there, save default settings
            else:
                with open(self.filepath, 'w') as f:
                    json.dump(self.settings, f, indent=2)
        except Exception:
            logger.error(f'Error while loading settings:\n{traceback.format_exc()}')
            # Save corrupted file on the side
            if os.path.isfile(self.filepath):
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                os.replace(self.filepath, f'{self.filepath.replace(".json","")}_corrupted ({now}).json')

        # Make sure all keys are here. This checks dictionaries recursively and fill missing keys.
        update_with_defaults(self.settings, self.default_settings)

    def save_settings(self):
        """ Save settings to an already definied filepath"""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info('Settings saved')
        except Exception:
            logger.error(f'Error while saving settings\n{traceback.format_exc()}')

    def settings_for_logs(self):
        """ Returns current settings that can be safely saved into logs"""
        out = self.settings.copy()
        out['aom_secret_key'] = "set" if out['aom_secret_key'] else None
        del out['rng_choices']
        del out['player_notes']
        out['twitchbot'] = out['twitchbot'].copy()
        out['twitchbot']['bot_oauth'] = "set" if out['twitchbot']['bot_oauth'] else None
        del out['twitchbot']['greetings']
        del out['twitchbot']['responses']
        return out

    def width_for_graphs(self):
        """ Checks whether the width needs to be changed for graphs"""
        if self.settings['show_charts'] and self.settings['width'] < 0.7:
            self.settings['width'] = 0.7


Setting_manager = CSettings()