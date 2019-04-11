import re

from .read_stata import read_stata
from .write_json import write_json


class Dataset:
    """
    Dataset allows the user to read, test and export data in different formats.
    
    Example:
        
        dataset = Dataset()
        dataset.read_stata("../input/dataset.dta")
        dataset.write_json("../output/dataset.json")
    """

    def __init__(self):
        self.dataset = None
        self.metadata = None

    def read_stata(self, dta_name):
        """
        Function to read data in stata format.
        
        Parameter:
        
        dta_name: Name of the data in stata format
        
        Example:
        
        dataset.read_stata("../input/dataset.dta")        
        """
        self.dataset, self.metadata = read_stata(dta_name)

    def write_json(
        self,
        output_name,
        analysis_unit="",
        period="",
        sub_type="",
        study="",
        metadata_de=""
    ):
        """
        Function to write statistics from data in json/html format.
        
        Parameter:
        
        output_name: Name of the output file
        file_type: Statistics are read out in json or html; Standard is "json"
        split: Name of the variable(s) for bivariate statistics; Standard is ""
        weight: Name of the weight variable; Standard is ""
        
        Example:
        
        dataset.write_json("../output/dataset.html", file_type="html", split="split", weight="weight") 
        """
        write_json(
            self.dataset,
            self.metadata,
            output_name,
            analysis_unit=analysis_unit,
            period=period,
            sub_type=sub_type,
            study=study,
            metadata_de=metadata_de
        )
