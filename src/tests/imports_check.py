import wlepmeister
from wlepmeister.src import main

def test_import():
    assert wlepmeister.__version__ 

def test_main_function():
    assert callable(main.main)
