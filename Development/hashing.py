import hashlib

def get_hash(file, sha=False):
    """ Returns MD5/SHA256 file hash for a file """
    with open(file, "rb") as f:
        bytesread = f.read()
        if sha:
            readable_hash = hashlib.sha3_256(bytesread).hexdigest()
        else:
            readable_hash = hashlib.md5(bytesread).hexdigest()

    return readable_hash
