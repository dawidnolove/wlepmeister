import unittest

try:
    import wlepmeister
    from wlepmeister import main
except ModuleNotFoundError:
    import src as wlepmeister
    from src import main


class ImportTests(unittest.TestCase):
    def test_import(self):
        self.assertTrue(wlepmeister.__version__)

    def test_main_function(self):
        self.assertTrue(callable(main.main))
