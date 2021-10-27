import os
import pathlib
import sys

import SCOFunctions.AppFunctions as AF


def truePath(file: str) -> str:
    """ Returns the path to the main directory regardless of the current working directory 
    For non-packaged run, this is assuming that MFilePath is in a direct subfolder of the main folder (hence double .parent)"""

    if AF.isCompiled():
        return os.path.normpath(os.path.join(AF.nuitka_exe_folder(), file))

    if AF.isFrozen():
        path = os.path.join(pathlib.Path(sys.executable).parent.absolute(), file)
        return os.path.normpath(path)

    path = os.path.join(pathlib.Path(__file__).parent.parent.absolute(), file)
    return os.path.normpath(path)


def innerPath(file: str) -> str:
    """ Gets path to a packaged file
    Takes care of cases when it's packaged with pyinstaller.
    """

    if AF.isCompiled():
        return os.path.normpath(os.path.join(AF.nuitka_exe_folder(), file))

    if AF.isFrozen():
        path = os.path.join(pathlib.Path(sys.executable).parent.absolute(), file)
        return os.path.normpath(path)

    return file
