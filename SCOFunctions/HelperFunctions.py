import os
import sys
import json
import string
import requests
import zipfile
import traceback
from pathlib import Path
from SCOFunctions.MFilePath import truePath
from SCOFunctions.MLogging import logclass


# Use ctypes.wintypes only on windows platform
if os.name == 'nt':
    import ctypes.wintypes
    from SCOFunctions.MRegistry import reg_add_to_startup, reg_get_startup_field_value, reg_delete_startup_field
else: 
    logger.info("Not a Windows operation system, won't use ctypes.wintypes or winreg" )


logger = logclass('HELP','INFO')
version_link = 'https://github.com/FluffyMaguro/SC2_Coop_overlay/raw/master/version.txt'


def write_permission_granted():
    """ Returns True if the app can write into its directory """
    permission_granted = True
    tfile = truePath('test_permission_file')
    try:
        with open(tfile, 'a') as f:
            f.write('.')
        os.remove(tfile)
    except:
        permission_granted = False
        logger.info(f'Permission error:\n{traceback.format_exc()}')

    return permission_granted


def add_to_startup(Add):
    """ Add to startup. Returns error string or None."""

    if not os.name == 'nt':
        return 'Not a Windows-type OS. Not adding to the startup!'

    if not getattr(sys, 'frozen', False):
        return 'App is not packaged. Not adding to the startup!'

    try:
        key = 'StarCraft Co-op Overlay'
        if Add:
            path = truePath('SCO.exe')
            logger.info(f'Adding {path} to registry as {key}')
            reg_add_to_startup(key, path)
        else:
            reg_delete_startup_field(key)
    except:
        logger.error(f'Failed to edit registry.\n{traceback.format_exc()}')
        return 'Error when adding the app to registry!'

    finally:
        return None


def new_version(current_version):
    """ Checks for a new version of the app. Returns a download link if a new version available. """
    try:
        data = json.loads(requests.get(version_link).text)
        logger.info(f'This version: {str(current_version)[0]}.{str(current_version)[1:]}. Most current live version: 1.{data["version"]}. ')
        if data['version'] > current_version:
            return data['download_link_1']
        else:
            return False
    except:
        logger.error('Failed to check for the new version')
        return False


def archive_is_corrupt(archive):
    """ Checks if an archive is corrupt"""
    print(f'Checking: {archive}')
    test = zipfile.ZipFile(archive).testzip()

    if test == None:
        return False
    return True


def extract_archive(file, targetdir):
    """ Extracts file to target directory """
    with zipfile.ZipFile(file, 'r') as f:
        f.extractall(targetdir)


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
