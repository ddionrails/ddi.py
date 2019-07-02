"""stata_to_json.py"""
__author__ = "Marius Pahl"

import pandas as pd
from .dataset import Dataset


def stata_to_json(study_name, input_csv, input_path, output_path, input_path_de=""):
    '''
    Input:
    study_name: Name of the study
    input_csv: Path to metadata csv
    input_path: path to data folder
    output_path: path to output folder
    input_path_de: path to german data folder (can be empty)

    This method reads stata file(s), transforms it in tabular data package and write it out.
    '''
    filereader = pd.read_csv(input_csv, delimiter=",", header=0)

    for data, analysis_unit, period, sub_type, boost in zip(
        filereader.filename,
        filereader.analysis_unit,
        filereader.period,
        filereader.sub_type,
        filereader.boost,
    ):
        dataset_1 = Dataset()
        try:
            dataset_1.read_stata(input_path + data + ".dta")
        except IOError:
            print("Unable to find " + data + ".dta in " + input_path + ".")
            continue

        metadata_de = ""
        if input_path_de != "":
            dataset_2 = Dataset()
            try:
                dataset_2.read_stata(input_path_de + data + ".dta")
                metadata_de = dataset_2.metadata
            except IOError:
                print("Unable to find " + data +
                      ".dta in " + input_path_de + ".")
                continue

        dataset_1.write_json(
            output_path + data + "_stats.json",
            analysis_unit=analysis_unit,
            period=period,
            sub_type=sub_type,
            boost=str(boost),
            study=study_name,
            metadata_de=metadata_de,
        )
