import unittest
import pandas
from ddi import statareader

class TestStataReader(unittest.TestCase):

    def test_read_stata(self):
        stata = statareader.read_stata("test/data/test1.dta")
        self.assertEqual(
            stata.data.__class__,
            pandas.core.frame.DataFrame
        )
        self.assertTrue(len(stata.meta) > 0)
