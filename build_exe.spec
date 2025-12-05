# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect customtkinter data files (themes, assets, etc.)
ctk_datas = collect_data_files('customtkinter')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.png', '.'),  # Include logo in root
        *ctk_datas,  # Include customtkinter assets
        ('algorithms', 'algorithms'),  # Include algorithms module
        ('config', 'config'),  # Include config module
        ('models', 'models'),  # Include models module
        ('ui', 'ui'),  # Include ui module
        ('utils', 'utils'),  # Include utils module
    ],
    hiddenimports=[
        'customtkinter',
        'numpy',
        'scipy',
        'scipy.optimize',
        'scipy.optimize.linear_sum_assignment',
        'pandas',
        'openpyxl',
        'tkinter',
        'PIL',
        'PIL._tkinter_finder',
    ] + collect_submodules('customtkinter'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OR_Problem_Solver',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see console output for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.png',  # Use logo as icon
)
