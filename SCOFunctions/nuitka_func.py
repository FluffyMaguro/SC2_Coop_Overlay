import pathlib
import sys


def is_compiled() -> bool:
    """ Checks whether the app is compiled by Nuitka"""
    return '__compiled__' in globals()


def exe_folder() -> str:
    """ Returns the folder of the executable"""
    return pathlib.Path(sys.argv[0]).parent.absolute()
