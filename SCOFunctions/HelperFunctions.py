import os
import string
from pathlib import Path

import requests

from SCOFunctions.MLogging import logclass

# Use ctypes.wintypes only on windows platform
if os.name == 'nt':
    import ctypes.wintypes
else: 
    logger.info("Not a Windows operation system, won't use ctypes.wintypes" )


logger = logclass('HELP','INFO')



def get_account_dir(path=None):
    """ Locates StarCraft account directory or returns one if it's good"""

    # If the one provided is good, just return it.
    if path != None and os.path.isdir(path) and 'StarCraft' in path:
        return path

    # On windows use Use ctypes.wintypes
    if os.name == 'nt':
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 1   # Get current, not default value
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        user_folder = buf.value.replace('Documents','')
    else:
        user_folder = os.path.abspath(os.path.expanduser('~'))
        if not os.path.isdir(user_folder):
            user_folder = Path.home()


    # If we have user folder, try finding the account section
    if os.path.isdir(user_folder):
        # Typical folder location
        account_path = os.path.join(user_folder,'Documents\\StarCraft II\\Accounts')
        if os.path.isdir(account_path):
            return account_path

        # One drive location
        account_path = os.path.join(user_folder,'OneDrive\\Documents\\StarCraft II\\Accounts')
        if os.path.isdir(account_path):
            return account_path

        # Check in all current user folders
        for root, directories, files in os.walk(user_folder):
            for file in files:
                if file.endswith('.SC2Replay') and 'StarCraft II\\Accounts' in root:
                    account_path = os.path.join(root,file).split('StarCraft II\\Accounts')[0]
                    account_path += 'StarCraft II\\Accounts'
                    return account_path


    # If we failed to locate the user folder check all available drives
    available_drives = [f'{d}:\\' for d in string.ascii_uppercase if os.path.exists(f'{d}:\\')]
    for drive in available_drives:
        for root, directories, files in os.walk(drive):
            for file in files:
                if 'StarCraft II\\Accounts' in root and not '\\Sandbox\\' in root and file.endswith('.SC2Replay'):
                    account_path = os.path.join(root,file).split('StarCraft II\\Accounts')[0]
                    account_path += 'StarCraft II\\Accounts'
                    return account_path

    logger.error('Failed to find any StarCraft II account directory')
    return ''


def validate_aom_account_key(account, key):
    """ Returns 'Success' for valid combination of account name and key, error (string) for invalid combination"""
    url = f'https://starcraft2coop.com/scripts/assistant/replay.php?test=1&username={account}&secretkey={key}'
    response = requests.get(url)
    return response.text
