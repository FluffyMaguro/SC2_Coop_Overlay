import os
import pathlib
import sys


def isWindows() -> bool:
    if os.name == 'nt':
        return True
    return False


def isFrozen() -> bool:
    """ Checks whether the app is frozen by Pyinstaller"""
    return bool(getattr(sys, 'frozen', False))


def isCompiled() -> bool:
    """ Checks whether the app is compiled by Nuitka"""
    return '__compiled__' in globals()


def nuitka_exe_folder():
    """ Returns the folder of the executable"""
    return pathlib.Path(sys.argv[0]).parent.absolute()


def app_type() -> str:
    """ Returns how the app is packaged

    Returns:
        'Nuitka' | 'Pyinstaller' | 'Script'
    """

    if isCompiled():
        return "Nuitka"
    if isFrozen():
        return "Pyinstaller"
    return "Script"
