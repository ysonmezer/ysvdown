# -*- mode: python ; coding: utf-8 -*-

# YS Video Downloader v2.7 - Defender-Optimized Build Spec
# EXE adı ve ikon düzeltildi

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# yt-dlp tüm alt modüllerini topla
yt_dlp_hidden = collect_submodules('yt_dlp')
yt_dlp_data = collect_data_files('yt_dlp')

block_cipher = None

a = Analysis(
    ['main.py'],  # Kaynak dosyanız (main.py veya main_improved.py)
    pathex=[],
    binaries=[],
    datas=[
        ('logo.ico', '.'),  # Logo dahil edilecek
    ] + yt_dlp_data,
    hiddenimports=[
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.postprocessor',
        'mutagen',
        'pycryptodome',
        'websockets',
        'brotli',
    ] + yt_dlp_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'numpy',
        'PIL',
        'PyQt5',
        'tkinter.test',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YS Video Downloader v2.7',  # ✅ EXE adı burada belirleniyor
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # ✅ Konsolu gizle
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.ico',  # ✅ İkon dosyası (proje klasöründe olmalı)
    version='file_version_info.txt',
    uac_admin=False,
    uac_uiaccess=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='YS Video Downloader v2.7',  # ✅ Klasör adı
)
