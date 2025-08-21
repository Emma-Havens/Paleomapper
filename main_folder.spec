# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

input_files = [('input/**', 'input'), ('shape_library.csv', '.')]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('/Users/emmahavens/opt/anaconda3/envs/geoenv/lib/libpython3.10.dylib', '.'),
        ('/Users/emmahavens/Documents/PlateTracker/ffmpeg', '.')],
    datas=collect_data_files('matplotlib') + input_files,  # Collect matplotlib data files
    hiddenimports=[
        'matplotlib.backends.backend_pdf',
        'matplotlib.backends.backend_qtagg',
        'matplotlib.backends.backend_agg',
        'scipy.special._cdflib',
        *[m for m in collect_submodules('PySide6') if 'QtAsyncio' not in m],
    ],
    hookspath=['/Users/emmahavens/Documents/PlateTracker/hook-matplotlib.py'],
    hooksconfig={},
    runtime_hooks=['fix-libpython.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
