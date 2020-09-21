import time

def wait_for_wake():
    """
    The goal of this function is to detect when a PC was awaken from sleeping.
    It will be checking time, and if there is a big discrepancy, it will return it.
    This function will be run on a separate thread.
    """

    while True:
        start = time.time()
        time.sleep(5)
        diff = time.time() - start
        if diff > 6:
            return diff