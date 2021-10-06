import winreg as reg

# This might need administrative access to edit the keys


def reg_add_to_startup(name, value):
    """ Adds a new field to the startup registry field.
    `name` is the name of the new field.
    `value` is its value (e.g. file path)"""
    key = reg.HKEY_CURRENT_USER
    key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"
    open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
    reg.SetValueEx(open, name, 0, reg.REG_SZ, f'"{value}"')
    reg.CloseKey(open)


def reg_get_startup_field_value(name: str):
    """ Returns value of given field in the startup registry key.

    Args:
        name: is the name of given field.
    Returns:
        If the field doesn't exist, returns `None`"""
    key = reg.HKEY_CURRENT_USER
    key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"
    open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
    response = None
    try:
        response = reg.QueryValueEx(open, name)[0]
    except Exception:
        pass
    finally:
        reg.CloseKey(open)
        return response


def reg_delete_startup_field(name: str):
    """ Deletes a field from the startup registry key.

    Args:
        name: is the name of that field"""
    key = reg.HKEY_CURRENT_USER
    key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"
    open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
    reg.DeleteValue(open, name)
    reg.CloseKey(open)
