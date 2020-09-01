import os

if os.name == 'nt':
    print('windows, using wintypes')
    import ctypes.wintypes


def get_account_dir(path):
    """ Locates StarCraft account directory """

    # If one is specified, use that
    if path != None and os.path.isdir(path):
        return path

    # Use ctypes.wintypes instead of expanduser to get current documents folder
    CSIDL_PERSONAL = 5       # My Documents
    SHGFP_TYPE_CURRENT = 1   # Get current, not default value
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    user_folder = buf.value.replace('Documents','')

    # Typical folder location
    account_path = os.path.join(user_folder,'Documents\\StarCraft II\\Accounts')
    if os.path.isdir(account_path):
        return account_path

    # One drive location
    account_path = os.path.join(user_folder,'OneDrive\\Documents\\StarCraft II\\Accounts')
    if os.path.isdir(account_path):
        return account_path

    # Check in all current user folders
    for root, directories, files in os.walk(user_folder):
        for file in files:
            if file.endswith('.SC2Replay') and 'StarCraft II\\Accounts' in root:
                account_path = os.path.join(root,file).split('StarCraft II\\Accounts')[0]
                account_path += 'StarCraft II\\Accounts'
                with open(config_file,'a') as f:
                    f.write(f'\nACCOUNTDIR = {account_path}')
                return account_path

    # Check in all drives
    available_drives = [f'{d}:\\' for d in string.ascii_uppercase if os.path.exists(f'{d}:\\')]
    for drive in available_drives:
        for root, directories, files in os.walk(drive):
            for file in files:
                if file.endswith('.SC2Replay') and 'StarCraft II\\Accounts' in root:
                    account_path = os.path.join(root,file).split('StarCraft II\\Accounts')[0]
                    account_path += 'StarCraft II\\Accounts'
                    with open(config_file,'a') as f:
                        f.write(f'\nACCOUNTDIR = {account_path}')
                    return account_path

    logger.error('Failed to find any StarCraft II account directory')
    return ''