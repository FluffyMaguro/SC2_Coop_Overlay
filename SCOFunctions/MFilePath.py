import os
import pathlib
import sys

import SCOFunctions.HelperFunctions as HF
import SCOFunctions.nuitka_func as NF


def truePath(file):
    """ Returns the path to the main directory regardless of the current working directory 
    For non-packaged run, this is assuming that MFilePath is in a direct subfolder of the main folder (hence double .parent)"""

    if NF.is_compiled():
        return os.path.normpath(os.path.join(NF.exe_folder(), file))

    if HF.isFrozen():
        path = os.path.join(pathlib.Path(sys.executable).parent.absolute(), file)
        return os.path.normpath(path)

    path = os.path.join(pathlib.Path(__file__).parent.parent.absolute(), file)
    return os.path.normpath(path)


def innerPath(file):
    """ Gets path to a packaged file
    Takes care of cases when it's packaged with pyinstaller.
    """

    if NF.is_compiled():
        return os.path.normpath(os.path.join(NF.exe_folder(), file))

    if HF.isFrozen():
        path = os.path.join(pathlib.Path(sys.executable).parent.absolute(), file)
        return os.path.normpath(path)

    return file
