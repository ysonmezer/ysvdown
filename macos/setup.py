from setuptools import setup

APP = ['../main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['yt_dlp', 'tkinter'],
    'includes': ['yt_dlp.extractor', 'yt_dlp.postprocessor'],
    'excludes': ['matplotlib', 'numpy', 'pandas', 'PyInstaller', 'PyQt5', 'PyQt6'],
    'iconfile': 'logo.icns',
    'semi_standalone': False,  # Tam standalone
    'site_packages': True,
    'plist': {
        'CFBundleName': 'YS Video Downloader',
        'CFBundleDisplayName': 'YS Video Downloader v2.8',
        'CFBundleVersion': '2.8.0',
        'CFBundleShortVersionString': '2.8.0',
        'LSMinimumSystemVersion': '12.0',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
