# fix_libpython.py
import os
import sys

def fix_libpython():
    libpython = os.path.join(sys._MEIPASS, 'libpython3.10.dylib')
    if os.path.exists(libpython):
        os.environ['DYLD_LIBRARY_PATH'] = sys._MEIPASS

fix_libpython()