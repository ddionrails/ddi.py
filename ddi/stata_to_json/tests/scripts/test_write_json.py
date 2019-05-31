import unittest
import pandas as pd
import numpy as np

from scripts.write_json import *

class TestWriteJson(unittest.TestCase):        
    
    def get_testdata(self):
        data = dict()
        
        # Testdata for categorical variables
        data["testcat"] = dict()
        data["testcat"]["name"] = "test"
        data["testcat"]["label"] = "categorical test variable"
        data["testcat"]["type"] = "cat"
        data["testcat"]["values"] = [{"value": -1, "label": "missing"}, {"value": 1, "label": "a"}, {"value": 2, "label": "b"}]
        data["testcat"]["element_de"] = ""
        data["testcat"]["file_csv"] = pd.DataFrame([-1,-1,1,1,2,2,1,np.nan,1], columns=['test'])
        
        # Testdata for string variables
        data["teststring"] = dict()
        data["teststring"]["name"] = "test"
        data["teststring"]["label"] = "string test variable"
        data["teststring"]["type"] = "string"
        data["teststring"]["element_de"] = ""
        data["teststring"]["file_csv"] = pd.DataFrame(["", "a", "b", ".", np.nan, "c", np.nan], columns=['test'])
        
        # Testdata for numerical variables
        data["testnumber"] = dict()
        data["testnumber"]["name"] = "test"
        data["testnumber"]["label"] = "numerical test variable"
        data["testnumber"]["type"] = "num"
        data["testnumber"]["element_de"] = ""
        data["testnumber"]["file_csv"] = pd.DataFrame([-1,-1,-2,5,10,10,15], columns=['test'])
        data["testnumber"]["names"] = ["Min.", "1st Qu.", "Median", "Mean", "3rd Qu.", "Max.", "valid", "invalid"]
        
        return data
        
    def get_testmetadata(self):
        m = dict()
        m["name"] = "teststudy"
        m["resources"] = list()      
        m["resources"].append(dict(path="testpath", schema=dict()))
        m["resources"][0]["schema"]["fields"] = list()
        
        catvar = dict()
        catvar["label"] = "label for testcat"
        catvar["type"] = "cat"
        catvar["name"] = "TESTCAT"
        catvar["values"] = list()
        catvar["values"].append(dict(label = "missing", value = -1))
        catvar["values"].append(dict(label = "a", value = 1))
        catvar["values"].append(dict(label = "b", value = 2))
        
        m["resources"][0]["schema"]["fields"].append(catvar)
        
        stringvar = dict()
        stringvar["label"] = "label for teststring"
        stringvar["type"] = "string"
        stringvar["name"] = "TESTSTRING"
        
        m["resources"][0]["schema"]["fields"].append(stringvar)
        
        numvar = dict()
        numvar["label"] = "label for testnumber"
        numvar["type"] = "num"
        numvar["name"] = "TESTNUMBER"
        
        m["resources"][0]["schema"]["fields"].append(numvar)
        
        return m    
    
    def test_uni_cat(self):
        data = self.get_testdata()
        element = data["testcat"]
        element_de = data["testcat"]["element_de"]
        file_csv = data["testcat"]["file_csv"]
        
        cat_dict = uni_cat(element, element_de, file_csv)
        
        assert cat_dict == OrderedDict(
                        [
                            ('frequencies', [2, 4, 2]),
                            ('values', ['-1', '1', '2']),
                            ('missings', ['true', 'false', 'false']), 
                            ('labels', ['missing', 'a', 'b'])
                        ]
                    )
    
    def test_uni_string(self):
        data = self.get_testdata()
        element = data["teststring"]
        file_csv = data["teststring"]["file_csv"]
        
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
                    
    def test_uni_number(self):
        data = self.get_testdata()
        element = data["testnumber"]
        file_csv = data["testnumber"]["file_csv"]
        
        number_dict = uni_number(element, file_csv)
        
        assert number_dict == OrderedDict(
                        [
                            ('frequencies', []), 
                            ('labels', []), 
                            ('missings', []), 
                            ('values', []), 
                            ('labels_de', [])
                        ]
                    )
        
    def test_stats_cat(self):
        data = self.get_testdata()
        element = data["testcat"]        
        file_csv = data["testcat"]["file_csv"]
        
        statistics = stats_cat(element, file_csv)
        
        assert statistics == OrderedDict(
                        [
                            ('names', ["valid", "invalid"]), 
                            ('values', ["6","3"])
                        ]
                    )
    
    def test_stats_string(self):
        data = self.get_testdata()
        element = data["teststring"]        
        file_csv = data["teststring"]["file_csv"]
        
        statistics = stats_string(element, file_csv)
        
        assert statistics == OrderedDict(
                        [
                            ('names', ["valid", "invalid"]), 
                            ('values', ["3","4"])
                        ]
                    )
    
    def test_stats_number(self):
        data = self.get_testdata()
        element = data["testnumber"]        
        file_csv = data["testnumber"]["file_csv"]
        
        names = data["testnumber"]["names"]
        
        statistics = stats_number(element, file_csv)
        
        assert statistics == OrderedDict(
                        [
                            ('names', ["Min.", "1st Qu.", "Median", "Mean", "3rd Qu.", "Max.", "valid", "invalid"]), 
                            ('values', ["5", "7.5", "10.0", "10.0", "12.5", "15", "4","3"])
                        ]
                    )
        
    
    def test_uni_statistics(self):
        pass
    
    def test_uni(self):
        pass
    
    def test_stat_dict(self):
        data = self.get_testdata()
        element = data["testcat"] 
        element_de = data["testcat"]["element_de"]
        file_csv = data["testcat"]["file_csv"]
        
        file_json = self.get_testmetadata()
        file_de_json = ""
        study = "teststudy"
        analysis_unit = "testunit"
        period = "2019"
        sub_type = "testtype"
        boost = 1
    
        x = stat_dict(
        element, 
        element_de,
        file_csv,
        file_json,
        file_de_json,
        analysis_unit,
        period,
        sub_type,
        boost,
        study)
        
        assert x == OrderedDict(
                                [
                                    ('study', 'teststudy'), 
                                    ('analysis_unit', 'testunit'), 
                                    ('period', '2019'), 
                                    ('sub_type', 'testtype'), 
                                    ('boost', 1), 
                                    ('dataset', 'teststudy'), 
                                    ('variable', 'test'), 
                                    ('name', 'test'), 
                                    ('name_cs', 'test'), 
                                    ('label', 'categorical test variable'), 
                                    ('scale', 'cat'), 
                                    ('categories', OrderedDict(
                                                        [
                                                            ('frequencies', [2, 4, 2]), 
                                                            ('values', ['-1', '1', '2']), 
                                                            ('missings', ['true', 'false', 'false']), 
                                                            ('labels', ['missing', 'a', 'b'])
                                                        ]
                                                    ))
                                ]
                            )
    
    def test_generate_stat(self):
        pass
    
    def test_write_json(self):
        pass
    

if __name__ == '__main__':
    unittest.main()
