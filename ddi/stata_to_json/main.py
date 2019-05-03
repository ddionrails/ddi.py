import os,sys
import pandas as pd
os.system("setup.sh")

from scripts import stata_to_json

stata_to_json(
    study_name="soep-core",
    input_csv="metadata/datasets.csv",
    input_path="input/teststudy/",
    input_path_de="",
    output_path="output/test/"
)

stata_to_json(
    study_name="soep-core",
    input_csv="metadata/datasets.csv",
    input_path="input/soep-core/",
    input_path_de="",
    output_path="output/soep-core/"
)