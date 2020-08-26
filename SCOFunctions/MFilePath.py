import os
import sys
import pathlib


def truePath(file):
    """ Returns the path to the main directory regardless of current working directory """
    
    if getattr(sys, 'frozen', False):
        path = os.path.join(pathlib.Path(sys.executable).parent.absolute(),file)
        print(f'App fronzen, returnig path: {path}')
        return path

    path = os.path.join(pathlib.Path(__file__).parent.parent.absolute(),file)    
    print(f'App NOT fronzen, returnig path: {path}')
    return path
