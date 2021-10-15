"""
This script makes packaging with Pyinstaller easier
Run the pyinstaller, cleans up, zips files.

"""

import json
import os
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

from useful_functions import get_hash, get_version, clear_pycache

app_version = get_version()
clear_pycache()

# Run pyinstaller
os.system('cmd /c "pyinstaller.exe'
          ' --noconsole'
          ' -i=src/OverlayIcon.ico'
          ' --add-data venv\Lib\site-packages\s2protocol;s2protocol'
          ' --add-data src;src'
          ' --add-data SCOFunctions\SC2Dictionaries\*.csv;SCOFunctions\SC2Dictionaries'
          ' --add-data SCOFunctions\SC2Dictionaries\*.txt;SCOFunctions\SC2Dictionaries'
          ' SCO.py"')

# Zip
file_name = f"SC2CoopOverlay ({app_version // 100}.{app_version % 100}).zip"
shutil.copytree('Layouts', 'dist/SCO/Layouts')
shutil.copy('Read me (Github).url', 'dist/SCO/Read me (Github).url')
shutil.move('dist/SCO', 'SCO')

to_zip = []
for root, directories, files in os.walk('SCO'):
    for file in files:
        to_zip.append(os.path.join(root, file))

print('Compressing files...')
with ZipFile(file_name, 'w', compression=ZIP_DEFLATED) as zip:
    for file in to_zip:
        zip.write(file, file[4:])  # The second argument makes it not appear in SCO/ directory in the zip file

# Cleanup
os.remove('SCO.spec')
for item in ('build', 'dist', '__pycache__', 'SCO'):
    shutil.rmtree(item)

# Hash
with open('version.txt', 'r') as f:
    version_data = json.load(f)

version_data['hash'] = get_hash(file_name, sha=True)
version_data['version'] = app_version

with open('version.txt', 'w') as f:
    json.dump(version_data, f, indent=2)
