import json
import os
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

from useful_functions import clear_pycache, get_hash, get_version

app_version = get_version()
clear_pycache()

# Run nuitka
os.system('cmd /c "python -m nuitka'
          ' --plugin-enable=pyqt5'
          ' --plugin-enable=multiprocessing'
          ' --standalone'
          ' --windows-disable-console'
          ' --windows-icon-from-ico=src/OverlayIcon.ico'
          ' --include-data-dir=src=src'
          ' --include-data-dir=Layouts=Layouts'
          ' --include-data-dir=venv/Lib/site-packages/s2protocol=s2protocol'
          ' --include-data-file=SCOFunctions/SC2Dictionaries/*.csv=SCOFunctions/SC2Dictionaries/'
          ' --include-data-file=SCOFunctions/SC2Dictionaries/*.txt=SCOFunctions/SC2Dictionaries/"'
          ' SCO.py')

# Copy readme
shutil.copy('Read me (Github).url', 'SCO.dist/Read me (Github).url')

# Copy QtWebEngineProcess.exe if it wasn't included automatically (depends on package versions)
webengine_path_venv = "venv/Lib/site-packages/PyQt5/Qt/bin/QtWebEngineProcess.exe"
webengine_path_pack = "SCO.dist/QtWebEngineProcess.exe"
if not os.path.isfile(webengine_path_pack):
    print("Copying QtWebEngineProcess.exe")
    shutil.copy(webengine_path_venv, webengine_path_pack)

# Zip
file_name = f"SC2CoopOverlay ({app_version // 100}.{app_version % 100}).zip"

to_zip = []
for root, directories, files in os.walk('SCO.dist'):
    for file in files:
        to_zip.append(os.path.join(root, file))

print('Compressing files...')
with ZipFile(file_name, 'w', compression=ZIP_DEFLATED) as zip:
    for file in to_zip:
        zip.write(file, file[9:])  # The second argument makes it not appear in SCO/ directory in the zip file

# Cleanup
for item in ('SCO.build', 'SCO.dist', 'dist'):
    if os.path.isdir(item):
        shutil.rmtree(item)

# Hash
with open('version.txt', 'r') as f:
    version_data = json.load(f)

version_data['hash'] = get_hash(file_name, sha=True)
version_data['version'] = app_version

with open('version.txt', 'w') as f:
    json.dump(version_data, f, indent=2)
