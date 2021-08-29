import hashlib
import os


def get_hash(file, sha=False):
    """ Returns MD5/SHA256 file hash for a file """
    with open(file, "rb") as f:
        bytesread = f.read()
        if sha:
            readable_hash = hashlib.sha3_256(bytesread).hexdigest()
        else:
            readable_hash = hashlib.md5(bytesread).hexdigest()

    return readable_hash


def get_version() -> int:
    """ Returns the app version"""
    path = os.path.abspath(os.path.join(os.getcwd(), 'SCO.py'))
    with open(path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if 'APPVERSION' in line:
            return int(line.split(' = ')[-1])

    raise Exception('App version not found')
