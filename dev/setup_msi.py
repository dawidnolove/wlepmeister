from cx_Freeze import setup, Executable

setup(
    name="Wlepmeister",
    version="9.12",
    description="",
    executables=[Executable("../src/main.py")],
    options={
        "build_exe": {
            "include_files": ["../media/icon_py_128.ico"]
        }
    }
)
