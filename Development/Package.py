"""
This script makes packaging with Pyinstaller easier
Run the pyinstaller, cleans up, zips files.

"""

import json
import os
import shutil
from zipfile import ZIP_BZIP2, ZipFile

from hashing import get_hash

# Clear __pycache__ from s2protocol folders
cache_folders = set()
for root, directories, files in os.walk(os.getcwd()):
    for directory in directories:
        if directory == '__pycache__':
            dir_path = os.path.join(root, directory)
            if 's2protocol' in root or 'websockets' in root:
                print(f'Removing: {dir_path}')
                shutil.rmtree(dir_path)

# Run pyinstaller
os.system('cmd /c "pyinstaller.exe'
          ' --noconsole'
          ' -i=src/OverlayIcon.ico'
          ' --add-data venv\Lib\site-packages\s2protocol;s2protocol'
          ' --add-data venv\Lib\site-packages\websockets;websockets'
          ' --add-data src;src'
          ' --add-data SCOFunctions\SC2Dictionaries\*.csv;SCOFunctions\SC2Dictionaries'
          ' --add-data SCOFunctions\SC2Dictionaries\*.txt;SCOFunctions\SC2Dictionaries'
          ' SCO.py"')

# Zip
file_name = f"SC2CoopOverlay (x.x).zip"
shutil.copytree('Layouts', 'dist/SCO/Layouts')
shutil.copy('Read me (Github).url', 'dist/SCO/Read me (Github).url')
shutil.move('dist/SCO', 'SCO')

to_zip = []
for root, directories, files in os.walk('SCO'):
    for file in files:
        to_zip.append(os.path.join(root, file))

print('Compressing files...')
with ZipFile(file_name, 'w', compression=ZIP_BZIP2) as zip:
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

with open('version.txt', 'w') as f:
    json.dump(version_data, f, indent=2)
