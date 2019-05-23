import unittest

from scripts.write_json import *

class TestWriteJson(unittest.TestCase):        
    
    def test_uni_string(self):
        element = dict()
        element["type"] = "string"
        file_csv = list()
        
        string_dict = uni_string(element, file_csv)
        
        assert string_dict == OrderedDict(
                        [
                            ('frequencies', []), 
                            ('labels', []), 
                            ('missings', []), 
                            ('values', []), 
                            ('labels_de', [])
                        ]
                    )

if __name__ == '__main__':
    unittest.main()
