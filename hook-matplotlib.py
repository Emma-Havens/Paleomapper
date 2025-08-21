# hook-matplotlib.py
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('matplotlib.backends') + \
               collect_submodules('matplotlib') + \
               ['scipy.special._cdflib']

datas = collect_data_files('matplotlib')