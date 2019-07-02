"""test_write_json.py"""
__author__ = "Marius Pahl"

import unittest
import tempfile
import pandas as pd
import numpy as np

from scripts.write_json import *


class TestWriteJson(unittest.TestCase):
    '''
    Tests for all methods from write_json.py
    '''

    def setUp(self):
        '''
        Set a TemporaryDirectory for the json testfile
        '''
        self.sandbox = tempfile.TemporaryDirectory()
        return super().setUp()

    @ staticmethod
    def get_testdatatable():
        '''
        Create a test dataframe
        '''
        data_table = pd.DataFrame()
        data_table["TESTCAT"] = [-1, -1, 1, 2, 1, np.nan, 1]
        data_table["TESTSTRING"] = ["", "a", "b", ".", np.nan, "c", np.nan]
        data_table["TESTNUMBER"] = [-1, -1, -2, 5, 10, 10, 15]
        data_table["TESTOTHER"] = [-1, "a", -2, 5, "b", np.nan, 15]

        return data_table

    @ staticmethod
    def get_testmetadata():
        '''
        Create test metadata
        '''
        metadata = dict()
        metadata["name"] = "teststudy"
        metadata["resources"] = list()
        metadata["resources"].append(dict(path="testpath", schema=dict()))
        metadata["resources"][0]["schema"]["fields"] = list()

        catvar = dict()
        catvar["label"] = "label for testcat"
        catvar["type"] = "cat"
        catvar["name"] = "TESTCAT"
        catvar["values"] = list()
        catvar["values"].append(dict(label="missing", value=-1))
        catvar["values"].append(dict(label="a", value=1))
        catvar["values"].append(dict(label="b", value=2))

        metadata["resources"][0]["schema"]["fields"].append(catvar)

        stringvar = dict()
        stringvar["label"] = "label for teststring"
        stringvar["type"] = "string"
        stringvar["name"] = "TESTSTRING"

        metadata["resources"][0]["schema"]["fields"].append(stringvar)

        numvar = dict()
        numvar["label"] = "label for testnumber"
        numvar["type"] = "number"
        numvar["name"] = "TESTNUMBER"

        metadata["resources"][0]["schema"]["fields"].append(numvar)

        othervar = dict()
        othervar["label"] = "label for other test type"
        othervar["type"] = ""
        othervar["name"] = "TESTOTHER"

        metadata["resources"][0]["schema"]["fields"].append(othervar)

        return metadata

    @ staticmethod
    def get_teststudy():
        '''
        Create a test study
        '''
        study = dict()

        study["file_de_json"] = ""
        study["study"] = "teststudy"
        study["analysis_unit"] = "testunit"
        study["period"] = "2019"
        study["sub_type"] = "testtype"
        study["boost"] = 1

        return study

    def test_uni_cat(self):
        '''
        Test for uni_cat
        '''
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTCAT"
            ),
            None,
        )
        element_de = ""
        file_csv = self.get_testdatatable()

        cat_dict = uni_cat(element, element_de, file_csv)

        assert cat_dict == OrderedDict(
            [
                ("frequencies", [2, 3, 1]),
                ("values", ["-1", "1", "2"]),
                ("missings", ["true", "false", "false"]),
                ("labels", ["missing", "a", "b"]),
            ]
        )

    @ staticmethod
    def test_uni_string():
        '''
        Test for uni_string
        '''

        string_dict = uni_string()

        assert string_dict == OrderedDict(
            [
                ("frequencies", []),
                ("labels", []),
                ("missings", []),
                ("values", []),
                ("labels_de", []),
            ]
        )

    @ staticmethod
    def test_uni_number():
        '''
        Test for uni_number
        '''

        number_dict = uni_number()

        assert number_dict == OrderedDict(
            [
                ("frequencies", []),
                ("labels", []),
                ("missings", []),
                ("values", []),
                ("labels_de", []),
            ]
        )

    def test_stats_cat(self):
        '''
        Test for stats_cat
        '''
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTCAT"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = stats_cat(element, file_csv)

        assert statistics == OrderedDict(
            [("names", ["valid", "invalid"]), ("values", ["4", "3"])]
        )

    def test_stats_string(self):
        '''
        Test for stats_string
        '''
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTSTRING"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = stats_string(element, file_csv)

        assert statistics == OrderedDict(
            [("names", ["valid", "invalid"]), ("values", ["3", "4"])]
        )

    def test_stats_number(self):
        '''
        Test for stats_number
        '''
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTNUMBER"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = stats_number(element, file_csv)

        assert statistics == OrderedDict(
            [
                (
                    "names",
                    [
                        "Min.",
                        "1st Qu.",
                        "Median",
                        "Mean",
                        "3rd Qu.",
                        "Max.",
                        "valid",
                        "invalid",
                    ],
                ),
                ("values", ["5", "7.5", "10.0",
                            "10.0", "12.5", "15", "4", "3"]),
            ]
        )

    def test_uni_statistics_cat(self):
        '''
        Test for categorical variables in uni_statistics
        '''
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTCAT"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = uni_statistics(element, file_csv)

        assert statistics == OrderedDict(
            [("names", ["valid", "invalid"]), ("values", ["4", "3"])]
        )

    def test_uni_statistics_string(self):
        '''
        Test for nominal variables in uni_statistics
        '''
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTSTRING"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = uni_statistics(element, file_csv)

        assert statistics == OrderedDict(
            [("names", ["valid", "invalid"]), ("values", ["3", "4"])]
        )

    def test_uni_statistics_number(self):
        '''
        Test for numerical variables in uni_statistics
        '''
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTNUMBER"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = uni_statistics(element, file_csv)

        assert statistics == OrderedDict(
            [
                (
                    "names",
                    [
                        "Min.",
                        "1st Qu.",
                        "Median",
                        "Mean",
                        "3rd Qu.",
                        "Max.",
                        "valid",
                        "invalid",
                    ],
                ),
                ("values", ["5", "7.5", "10.0",
                            "10.0", "12.5", "15", "4", "3"]),
            ]
        )

    def test_uni_statistics_other(self):
        '''
        Test for other variables in uni_statistics
        '''
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTOTHER"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = uni_statistics(element, file_csv)

        assert statistics == dict()

    def test_uni_testcat(self):
        '''
        Test for categorical variables in uni
        '''
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTCAT"
            ),
            None,
        )
        element_de = ""
        file_csv = self.get_testdatatable()

        cat_dict = uni(element, element_de, file_csv)

        assert cat_dict == OrderedDict(
            [
                ("frequencies", [2, 3, 1]),
                ("values", ["-1", "1", "2"]),
                ("missings", ["true", "false", "false"]),
                ("labels", ["missing", "a", "b"]),
            ]
        )

    def test_uni_teststring(self):
        '''
        Test for nominal variables in uni
        '''
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTSTRING"
            ),
            None,
        )
        element_de = ""
        file_csv = self.get_testdatatable()

        string_dict = uni(element, element_de, file_csv)

        assert string_dict == OrderedDict(
            [
                ("frequencies", []),
                ("labels", []),
                ("missings", []),
                ("values", []),
                ("labels_de", []),
            ]
        )

    def test_uni_testnumber(self):
        '''
        Test for numerical variables in uni
        '''
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTNUMBER"
            ),
            None,
        )
        element_de = ""
        file_csv = self.get_testdatatable()

        number_dict = uni(element, element_de, file_csv)

        assert number_dict == OrderedDict(
            [
                ("frequencies", []),
                ("labels", []),
                ("missings", []),
                ("values", []),
                ("labels_de", []),
            ]
        )

    def test_uni_testother(self):
        '''
        Test for other variables in uni
        '''
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTOTHER"
            ),
            None,
        )
        element_de = ""
        file_csv = self.get_testdatatable()

        other_dict = uni(element, element_de, file_csv)

        assert other_dict == dict()

    def test_stat_dict(self):
        '''
        Test for stat_dict
        '''
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTCAT"
            ),
            None,
        )
        element_de = ""
        file_csv = self.get_testdatatable()

        study_information = self.get_teststudy()
        file_json = self.get_testmetadata()

        study = study_information["study"]
        analysis_unit = study_information["analysis_unit"]
        period = study_information["period"]
        sub_type = study_information["sub_type"]
        boost = study_information["boost"]

        generated_data = stat_dict(
            element,
            element_de,
            file_csv,
            file_json,
            analysis_unit,
            period,
            sub_type,
            boost,
            study,
        )

        assert generated_data == OrderedDict(
            [
                ("study", "teststudy"),
                ("analysis_unit", "testunit"),
                ("period", "2019"),
                ("sub_type", "testtype"),
                ("boost", 1),
                ("dataset", "teststudy"),
                ("variable", "testcat"),
                ("name", "testcat"),
                ("name_cs", "TESTCAT"),
                ("label", "label for testcat"),
                ("scale", "cat"),
                (
                    "categories",
                    OrderedDict(
                        [
                            ("frequencies", [2, 3, 1]),
                            ("values", ["-1", "1", "2"]),
                            ("missings", ["true", "false", "false"]),
                            ("labels", ["missing", "a", "b"]),
                        ]
                    ),
                ),
            ]
        )

    def test_generate_stat(self):
        '''
        Test for generate_stat
        '''
        data = self.get_testdatatable()
        study_information = self.get_teststudy()
        file_json = self.get_testmetadata()

        file_de_json = study_information["file_de_json"]
        study = study_information["study"]
        analysis_unit = study_information["analysis_unit"]
        period = study_information["period"]
        sub_type = study_information["sub_type"]
        boost = study_information["boost"]

        generated_data = generate_stat(
            data, file_json, file_de_json, analysis_unit, period, sub_type, boost, study
        )

        assert generated_data == OrderedDict(
            [
                (
                    "testcat",
                    OrderedDict(
                        [
                            ("study", "teststudy"),
                            ("analysis_unit", "testunit"),
                            ("period", "2019"),
                            ("sub_type", "testtype"),
                            ("boost", 1),
                            ("dataset", "teststudy"),
                            ("variable", "testcat"),
                            ("name", "testcat"),
                            ("name_cs", "TESTCAT"),
                            ("label", "label for testcat"),
                            ("scale", "cat"),
                            (
                                "categories",
                                OrderedDict(
                                    [
                                        ("frequencies", [2, 3, 1]),
                                        ("values", ["-1", "1", "2"]),
                                        ("missings", [
                                         "true", "false", "false"]),
                                        ("labels", ["missing", "a", "b"]),
                                    ]
                                ),
                            ),
                        ]
                    ),
                ),
                (
                    "teststring",
                    OrderedDict(
                        [
                            ("study", "teststudy"),
                            ("analysis_unit", "testunit"),
                            ("period", "2019"),
                            ("sub_type", "testtype"),
                            ("boost", 1),
                            ("dataset", "teststudy"),
                            ("variable", "teststring"),
                            ("name", "teststring"),
                            ("name_cs", "TESTSTRING"),
                            ("label", "label for teststring"),
                            ("scale", "str"),
                            (
                                "categories",
                                OrderedDict(
                                    [
                                        ("frequencies", []),
                                        ("labels", []),
                                        ("missings", []),
                                        ("values", []),
                                        ("labels_de", []),
                                    ]
                                ),
                            ),
                            (
                                "statistics",
                                OrderedDict(
                                    [
                                        ("names", ["valid", "invalid"]),
                                        ("values", ["3", "4"]),
                                    ]
                                ),
                            ),
                        ]
                    ),
                ),
                (
                    "testnumber",
                    OrderedDict(
                        [
                            ("study", "teststudy"),
                            ("analysis_unit", "testunit"),
                            ("period", "2019"),
                            ("sub_type", "testtype"),
                            ("boost", 1),
                            ("dataset", "teststudy"),
                            ("variable", "testnumber"),
                            ("name", "testnumber"),
                            ("name_cs", "TESTNUMBER"),
                            ("label", "label for testnumber"),
                            ("scale", "num"),
                            (
                                "categories",
                                OrderedDict(
                                    [
                                        ("frequencies", []),
                                        ("labels", []),
                                        ("missings", []),
                                        ("values", []),
                                        ("labels_de", []),
                                    ]
                                ),
                            ),
                        ]
                    ),
                ),
                (
                    "testother",
                    OrderedDict(
                        [
                            ("study", "teststudy"),
                            ("analysis_unit", "testunit"),
                            ("period", "2019"),
                            ("sub_type", "testtype"),
                            ("boost", 1),
                            ("dataset", "teststudy"),
                            ("variable", "testother"),
                            ("name", "testother"),
                            ("name_cs", "TESTOTHER"),
                            ("label", "label for other test type"),
                            ("scale", ""),
                            ("categories", OrderedDict()),
                            ("statistics", {}),
                        ]
                    ),
                ),
            ]
        )

    def test_write_json(self):
        '''
        Test for write_json
        '''
        data = self.get_testdatatable()
        study_information = self.get_teststudy()
        metadata = self.get_testmetadata()

        metadata_de = study_information["file_de_json"]

        analysis_unit = study_information["analysis_unit"]
        period = study_information["period"]
        sub_type = study_information["sub_type"]
        boost = study_information["boost"]
        study = study_information["study"]

        filename = self.sandbox.name +"/test.json"

        write_json(
            data,
            metadata,
            filename,
            analysis_unit,
            period,
            sub_type,
            boost,
            study,
            metadata_de,
        )

        with open(filename) as json_file:
            output = json.load(json_file)

        assert output == {
            "testcat": {
                "study": "teststudy",
                "analysis_unit": "testunit",
                "period": "2019",
                "sub_type": "testtype",
                "boost": 1,
                "dataset": "teststudy",
                "variable": "testcat",
                "name": "testcat",
                "name_cs": "TESTCAT",
                "label": "label for testcat",
                "scale": "cat",
                "categories": {
                    "frequencies": [2, 3, 1],
                    "values": ["-1", "1", "2"],
                    "missings": ["true", "false", "false"],
                    "labels": ["missing", "a", "b"],
                },
            },
            "teststring": {
                "study": "teststudy",
                "analysis_unit": "testunit",
                "period": "2019",
                "sub_type": "testtype",
                "boost": 1,
                "dataset": "teststudy",
                "variable": "teststring",
                "name": "teststring",
                "name_cs": "TESTSTRING",
                "label": "label for teststring",
                "scale": "str",
                "categories": {
                    "frequencies": [],
                    "labels": [],
                    "missings": [],
                    "values": [],
                    "labels_de": [],
                },
                "statistics": {"names": ["valid", "invalid"], "values": ["3", "4"]},
            },
            "testnumber": {
                "study": "teststudy",
                "analysis_unit": "testunit",
                "period": "2019",
                "sub_type": "testtype",
                "boost": 1,
                "dataset": "teststudy",
                "variable": "testnumber",
                "name": "testnumber",
                "name_cs": "TESTNUMBER",
                "label": "label for testnumber",
                "scale": "num",
                "categories": {
                    "frequencies": [],
                    "labels": [],
                    "missings": [],
                    "values": [],
                    "labels_de": [],
                },
            },
            "testother": {
                "study": "teststudy",
                "analysis_unit": "testunit",
                "period": "2019",
                "sub_type": "testtype",
                "boost": 1,
                "dataset": "teststudy",
                "variable": "testother",
                "name": "testother",
                "name_cs": "TESTOTHER",
                "label": "label for other test type",
                "scale": "",
                "categories": {},
                "statistics": {},
            },
        }

    def tearDown(self):
        '''
        Clean TemporaryDirectory
        '''
        self.sandbox.cleanup()
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
