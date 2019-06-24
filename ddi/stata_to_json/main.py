"""main.py"""
__author__ = "Marius Pahl"

import os
from scripts.stata_to_json import stata_to_json

# Execute setup.py
os.system("./setup.sh")

stata_to_json(
    study_name="soep-core",
    input_csv="metadata/datasets.csv",
    input_path="input/teststudy/",
    input_path_de="",
    output_path="output/test/",
)

stata_to_json(
    study_name="soep-core",
    input_csv="metadata/datasets.csv",
    input_path="input/soep-core/",
    input_path_de="",
    output_path="output/soep-core/",
)
