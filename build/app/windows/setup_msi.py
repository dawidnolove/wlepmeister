from pathlib import Path

from cx_Freeze import setup, Executable

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parents[2]
MAIN = ROOT_DIR / "src" / "wlepmeister" / "app.py"
ICON = ROOT_DIR / "assets" / "icon_py_128.ico"
ASSETS_DIR = ROOT_DIR / "assets"

setup(
    name="Wlepmeister",
    version="9.12",
    description="",
    executables=[Executable(str(MAIN), icon=str(ICON))],
    options={
        "build_exe": {
            "include_files": [str(ASSETS_DIR)]
        }
    }
)
