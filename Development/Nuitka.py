import os
import shutil
from zipfile import ZipFile, ZIP_BZIP2

from useful_functions import get_version

app_version = get_version()

# Clear __pycache__ from s2protocol folders
cache_folders = set()
for root, directories, files in os.walk(os.getcwd()):
    for directory in directories:
        if directory == '__pycache__':
            dir_path = os.path.join(root, directory)
            if 's2protocol' in root or 'websockets' in root:
                print(f'Removing: {dir_path}')
                shutil.rmtree(dir_path)

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

# Zip
file_name = f"SC2CoopOverlay_nuitka ({app_version // 100}.{app_version % 100}).zip"
shutil.copy('Read me (Github).url', 'SCO.dist/Read me (Github).url')

to_zip = []
for root, directories, files in os.walk('SCO.dist'):
    for file in files:
        to_zip.append(os.path.join(root, file))

print('Compressing files...')
with ZipFile(file_name, 'w', compression=ZIP_BZIP2) as zip:
    for file in to_zip:
        zip.write(file, file[9:])  # The second argument makes it not appear in SCO/ directory in the zip file

# Cleanup
for item in ('SCO.build', 'SCO.dist', 'dist'):
    if os.path.isdir(item):
        shutil.rmtree(item)
