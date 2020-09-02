import os
import sys
import pathlib


def truePath(file):
    """ Returns the path to the main directory regardless of the current working directory 
    For non-packaged run, this is assuming that MFilePath is in a direct subfolder of the main folder (hence double .parent)"""
    
    if getattr(sys, 'frozen', False):
        path = os.path.join(pathlib.Path(sys.executable).parent.absolute(),file)
        return path

    path = os.path.join(pathlib.Path(__file__).parent.parent.absolute(),file)    
    return path


def innerPath(file):
    """ Gets path to a packaged file
    Takes care of cases when it's packaged with pyinstaller.
    """

    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, file)

    return file