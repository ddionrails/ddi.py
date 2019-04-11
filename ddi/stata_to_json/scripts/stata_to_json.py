import logging
import os
import sys

import pandas as pd
from .dataset import Dataset

def stata_to_json(
    study_name, input_csv, input_path, output_path, input_path_de=""
):
    filereader = pd.read_csv(input_csv, delimiter=",", header=0)

    for data, analysis_unit, period, sub_type in zip(
        filereader.filename,
        filereader.analysis_unit,
        filereader.period,
        filereader.sub_type,
    ):
        d1 = Dataset()
        try:
            d1.read_stata(input_path + data + ".dta")
        except:
            print("Unable to find " + data + ".dta in " + input_path + ".")
            continue

        metadata_de = ""
        if input_path_de != "":
            d2 = Dataset()
            try:
                d2.read_stata(input_path_de + data + ".dta")
                metadata_de = d2.metadata
            except:
                print(
                    "Unable to find " + data + ".dta in " + input_path_de + "."
                )
                continue

        d1.write_json(
            output_path + data + "_stats.json",
            analysis_unit=analysis_unit,
            period=period,
            sub_type=sub_type,
            study=study_name,
            metadata_de=metadata_de,
        )
