import unittest
from ddi import statareader

class TestStataReader(unittest.TestCase):

    def test_read_stata(self):
        ddi = statareader.read_stata("test/data/test1.dta")
        ddi.add_statistics()
