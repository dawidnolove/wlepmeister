from setuptools import setup

APP = ['src/main.py']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'media/icon_py_128.ico',  # jeśli chcesz ikonę
    'includes': [],
    'resources': ['media/icon_py_128.ico']  # dodatkowe zasoby
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
