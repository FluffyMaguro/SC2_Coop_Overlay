import datetime
import hashlib
import json
import os
import string
import sys
import traceback
import zipfile
from pathlib import Path
from typing import Dict, Optional, Union

import psutil
import requests

from SCOFunctions.MFilePath import innerPath, truePath
from SCOFunctions.MLogging import logclass
from SCOFunctions.nuitka_func import is_compiled

logger = logclass('HELP', 'INFO')
version_link = 'https://raw.githubusercontent.com/FluffyMaguro/SC2_Coop_overlay/master/version.txt'


def isWindows() -> bool:
    if os.name == 'nt':
        return True
    return False


# Use ctypes.wintypes and regirsty stuff only on windows platform
if isWindows():
    import ctypes.wintypes

    from SCOFunctions.MRegistry import (reg_add_to_startup,
                                        reg_delete_startup_field,
                                        reg_get_startup_field_value)
else:
    logger.info("Not a Windows operation system, won't use ctypes.wintypes or winreg")


def isFrozen() -> bool:
    """ Checks whether the app is frozen by Pyinstaller"""
    return bool(getattr(sys, 'frozen', False))


def app_type() -> str:
    """ Returns how the app is packaged

    Returns:
        'Nuitka' | 'Pyinstaller' | 'Script'
    """

    if is_compiled():
        return "Nuitka"
    if isFrozen():
        return "Pyinstaller"
    return "Script"


def get_hash(file: str, sha: bool = False) -> Optional[str]:
    """ Returns MD5/SHA256 file hash for a file """
    try:
        with open(file, "rb") as f:
            bytesread = f.read()
            if sha:
                readable_hash = hashlib.sha3_256(bytesread).hexdigest()
            else:
                readable_hash = hashlib.md5(bytesread).hexdigest()

        return readable_hash
    except Exception:
        logger.error(traceback.format_exc())
        return None


def write_permission_granted() -> bool:
    """ Returns True if the app can write into its directory """
    permission_granted = True
    tfile = truePath('test_permission_file')
    try:
        with open(tfile, 'a') as f:
            f.write('.')
        os.remove(tfile)
    except Exception:
        permission_granted = False
        logger.info(f'Permission error:\n{traceback.format_exc()}')

    return permission_granted


def get_region(handle: str) -> str:
    """ Retuns region based on player handle"""
    try:
        region_dict = {1: 'NA', 2: 'EU', 3: 'KR', 5: 'CN', 98: 'PTR'}
        s = handle.split("-S2-")[0]
        return region_dict.get(int(s), "?")
    except Exception:
        logger.error(traceback.format_exc())
        return "?"


def strtime(t: Union[int, float], show_seconds: bool = False) -> str:
    """ Returns formatted string 
    X days, Y hours, Z minutes
    """
    days, delta = divmod(t, 86400)
    hours, delta = divmod(delta, 3600)
    minutes, seconds = divmod(delta, 60)

    s = []
    if days:
        s.append(f"{days:.0f} days")
    if hours:
        s.append(f"{hours:.0f} hours")
    if minutes or not show_seconds:
        s.append(f"{minutes:.0f} minutes")
    if show_seconds:
        s.append(f"{seconds:.0f} seconds")
    return " ".join(s)


def get_time_difference(date: str) -> str:
    """ Returns time difference from now"""
    now = datetime.datetime.now()
    try:
        game_time = datetime.datetime.strptime(date, '%Y:%m:%d:%H:%M:%S')
    except Exception:
        logger.error(f"Failed to parse player date\n{date}\n{traceback.format_exc()}")
        return ""
    delta = (now - game_time).total_seconds()
    return f"{strtime(delta)} ago"


def app_running_multiple_instances() -> bool:
    """ Returns True if the app is running multiple instances.
    Normally there are two instances of SCO.exe running. """
    running = 0
    for pid in psutil.pids():
        try:
            process = psutil.Process(pid)
            if process.name() == 'SCO.exe':
                running += 1
        except Exception:
            pass

    return running > 1


def create_shortcut() -> None:
    """ Creates a shortcut to desktop"""

    if not isFrozen() or not isWindows():
        return

    shortcut_location = os.path.normpath(os.path.join(os.path.expanduser('~'), 'Desktop', 'SCO.url'))
    icon_location = os.path.abspath(innerPath('src/OverlayIcon.ico'))
    exe_location = truePath('SCO.exe')
    script  = [
    f'''echo [InternetShortcut] >> "{shortcut_location}"''',
    f'''echo URL="{exe_location}" >> "{shortcut_location}"''',
    f'''echo IconFile="{icon_location}" >> "{shortcut_location}"''',
    f'''echo IconIndex=0 >> "{shortcut_location}"'''] # yapf: disable

    script_to_show = '\n'.join(script)
    logger.info(f"Runnig script to create a desktop shortcut: \n{script_to_show}")
    for i in script:
        os.popen(i).read()  # Compared to os.system this doesn't open a console window when the app is packaged


def add_to_startup(Add: bool) -> Optional[str]:
    """ Add to startup. Returns error string or None."""

    if not isWindows() and Add:
        return 'Not a Windows-type OS. Not adding to the startup!'

    if not isFrozen() and Add:
        return 'App is not packaged. Not adding to the startup!'

    if not isWindows():
        return None

    try:
        key = 'StarCraft Co-op Overlay'
        path = truePath('SCO.exe')
        if Add:
            logger.info(f'Adding {path} to registry as {key}')
            reg_add_to_startup(key, path)
        elif reg_get_startup_field_value(key) is not None:
            logger.info(f'Removing {path} from registry as {key}')
            reg_delete_startup_field(key)
    except Exception:
        logger.error(f'Failed to edit registry.\n{traceback.format_exc()}')
        return 'Error when adding the app to registry!'

    finally:
        return None


def new_version(current_version: int) -> Union[bool, Dict[str, str]]:
    """ Checks for a new version of the app. Returns a download link if a new version available. """
    try:
        data = json.loads(requests.get(version_link).text)
        logger.info(f'This version: {str(current_version)[0]}.{str(current_version)[1:]}. Most current live version: {data["version"]}. ')
        if data['version'] > current_version:
            return {"link": data['download_link_1'], "hash": data['hash']}
        else:
            return False
    except Exception:
        logger.error('Failed to check for the new version')
        return False


def archive_is_corrupt(archive: str) -> bool:
    """ Checks if an archive is corrupt"""
    print(f'Checking: {archive}')
    test = zipfile.ZipFile(archive).testzip()

    if test is None:
        return False
    return True


def extract_archive(file_path: str, targetdir: str) -> None:
    """ Extracts file to target directory """
    with zipfile.ZipFile(file_path, 'r') as f:
        f.extractall(targetdir)


def get_account_dir(path: Optional[str] = None) -> str:
    """ Locates StarCraft account directory or returns one if it's good"""

    # If the one provided is good, just return it.
    if path is not None and os.path.isdir(path) and 'StarCraft' in path:
        return path

    # On windows use Use ctypes.wintypes
    if isWindows():
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 1  # Get current, not default value
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        user_folder = buf.value.replace('Documents', '')
    else:
        user_folder = os.path.abspath(os.path.expanduser('~'))
        if not os.path.isdir(user_folder):
            user_folder = Path.home()

    # If we have user folder, try finding the account section
    if os.path.isdir(user_folder):
        # Typical folder location
        account_path = os.path.abspath(os.path.join(user_folder, 'Documents', 'StarCraft II', 'Accounts'))
        if os.path.isdir(account_path):
            return account_path

        # Mac
        account_path = os.path.abspath(os.path.join(user_folder, 'Library', 'Application Support', 'Blizzard', 'StarCraft II', 'Accounts'))
        if os.path.isdir(account_path):
            return account_path

        # One drive location
        if hasattr(os.environ, "ONEDRIVE"):
            account_path = os.path.abspath(os.path.join(os.environ["ONEDRIVE"], 'Documents', 'StarCraft II', 'Accounts'))
            if os.path.isdir(account_path):
                return account_path

        # Check in all current user folders
        for root, _, files in os.walk(user_folder):
            for file in files:
                if file.endswith('.SC2Replay') and 'StarCraft II\\Accounts' in root:
                    account_path = os.path.join(root, file).split('StarCraft II\\Accounts')[0]
                    account_path += 'StarCraft II\\Accounts'
                    return os.path.abspath(account_path)

    # If we failed to locate the user folder check all available drives
    available_drives = [f'{d}:\\' for d in string.ascii_uppercase if os.path.exists(f'{d}:\\')]
    for drive in available_drives:
        for root, directories, files in os.walk(drive):
            for file in files:
                if 'StarCraft II\\Accounts' in root and not '\\Sandbox\\' in root and file.endswith('.SC2Replay'):
                    account_path = os.path.join(root, file).split('StarCraft II\\Accounts')[0]
                    account_path += 'StarCraft II\\Accounts'
                    return os.path.abspath(account_path)

    logger.error('Failed to find any StarCraft II account directory')
    return ''


def validate_aom_account_key(account: str, key: str) -> str:
    """ Returns 'Success' for valid combination of account name and key, error (string) for invalid combination"""
    url = f'https://starcraft2coop.com/scripts/assistant/replay.php?test=1&username={account}&secretkey={key}'
    response = requests.get(url)
    return response.text
