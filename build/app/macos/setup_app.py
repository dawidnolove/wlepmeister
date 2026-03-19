from pathlib import Path
import sys

from setuptools import setup

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parents[2]
APP = [str(ROOT_DIR / "src" / "wlepmeister" / "app.py")]
ICON = ROOT_DIR / "assets" / "icon_py_128.ico"
ASSETS_DIR = ROOT_DIR / "assets"

# modulegraph can hit deep recursion on large dependency graphs
sys.setrecursionlimit(10000)
OPTIONS = {
    "argv_emulation": True,
    "iconfile": str(ICON),  # jeśli chcesz ikonę
    "includes": [],
    "packages": ["pymongo"],
    "excludes": ["pymongo._cmessage"],
    "resources": [str(ASSETS_DIR)],  # dodatkowe zasoby
}

setup(
    name="Wlepmeister",
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
