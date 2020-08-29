"""
This script makes packaging with Pyinstaller easier
Run the pyinstaller, cleans up, zips files.

"""

import os
import shutil
from zipfile import ZipFile 


# Clear __pycache__ from s2protocol folders
cache_folders = set()
for root, directories, files in os.walk(os.getcwd()):
    for directory in directories:
        if directory == '__pycache__':
            dir_path = os.path.join(root,directory)
            if 's2protocol' in root:
                print(f'Removing: {dir_path}')
                shutil.rmtree(dir_path)


# Run pyinstaller
os.system('cmd /c "pyinstaller.exe --onefile --noconsole -i=src/OverlayIcon.ico --add-data venv\Lib\site-packages\s2protocol;s2protocol --add-data src\*.ico;src --add-data SCOFunctions\SC2Dictionaries\*.csv;SCOFunctions\SC2Dictionaries --add-data SCOFunctions\SC2Dictionaries\*.txt;SCOFunctions\SC2Dictionaries SCO.py"')

# Move SCO.exe
os.replace('dist/SCO.exe','SCO.exe')

# Zip
file_name = f"SC2CoopOverlay (1.x).zip"

# Backup config, and zip modified bersion
shutil.copy('SCO_config.ini', 'SCO_config_BK.ini')

# Rename default
shutil.copy('SCO_config_default.ini', 'SCO_config.ini')

to_zip = ['SCO.exe','SCO_config.ini','Read me (Github).url']
to_zip.extend([f'Layouts/{f}' for f in os.listdir('Layouts')])
to_zip.extend([f'Layouts/Icons/{f}' for f in os.listdir('Layouts/Icons')])
to_zip.extend([f'Layouts/Commanders/{f}' for f in os.listdir('Layouts/Commanders')])

with ZipFile(file_name,'w') as zip: 
        for file in to_zip: 
            zip.write(file) 

# Restore original config
os.replace('SCO_config_BK.ini', 'SCO_config.ini')

# Cleanup
os.remove('SCO.spec')
for item in {'build','dist','__pycache__'}:
    shutil.rmtree(item)

