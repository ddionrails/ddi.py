import json
import math
import os
import re
from collections import Counter, OrderedDict

import yaml
from jinja2 import Template

import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

def uni_cat(elem, elem_de, file_csv):
    """Generate dict with frequencies and labels for categorical variables"""

    frequencies = []
    values = []
    missings = []
    labels = []

    if elem_de != "":
        labels_de = []

        value_count = file_csv[elem["name"]].value_counts()
        for i, (value, value_de) in enumerate(zip(elem["values"], elem_de["values"])):
            try:
                frequencies.append(int(value_count[value["value"]]))
            except:
                frequencies.append(0)
            labels.append(value["label"])
            labels_de.append(value_de["label"])
            if value["value"] >= 0:
                missings.append("False")
            else:
                missings.append("True")
            values.append(value["value"])
    else:
        value_count = file_csv[elem["name"]].value_counts()
        for i, value in enumerate(elem["values"]):
            try:
                frequencies.append(int(value_count[value["value"]]))
            except:
                frequencies.append(0)
            labels.append(value["label"])
            if value["value"] >= 0:
                missings.append("False")
            else:
                missings.append("True")
            values.append(value["value"])
    """
    missing_count = sum(i<0 for i in file_csv[elem["name"]])
    """

    cat_dict = OrderedDict(
        [
            ("frequencies", frequencies),
            ("values", values),
            ("missings", missings),
            ("labels", labels),
        ]
    )
    if elem_de != "":
        cat_dict["labels_de"] = labels_de

    return cat_dict


def uni_string(elem, file_csv):
    """Generate dict with frequencies for nominal variables"""

    frequencies = []
    missings = []

    len_unique = len(file_csv[elem["name"]].unique())
    len_missing = 0
    for i in file_csv[elem["name"]].unique():
        if "-1" in str(i):
            len_unique -= 1
            len_missing += 1
        elif "-2" in str(i):
            len_unique -= 1
            len_missing += 1
        elif "-3" in str(i):
            len_unique -= 1
            len_missing += 1
        elif "nan" in str(i):
            len_unique -= 1
            len_missing += 1
    frequencies.append(len_unique)
    missings.append(len_missing)

    string_dict = OrderedDict([("frequencies", frequencies), ("missings", missings)])

    return string_dict


def uni_number(elem, file_csv, num_density_elements=20):
    """Generate dict with frequencies for numerical variables"""

    if (
        file_csv[elem["name"]].dtype == "object"
        or file_csv[elem["name"]].dtype == "object"
    ):
        file_csv[elem["name"]] = pd.to_numeric(file_csv[elem["name"]])

    # missings
    missings = OrderedDict([("frequencies", []), ("labels", []), ("values", [])])

    density = []
    total = []
    valid = []
    missing = []

    # min and max
    try:
        min_val = min(i for i in file_csv[elem["name"]] if i >= 0).astype(np.float64)
        max_val = max(i for i in file_csv[elem["name"]] if i >= 0).astype(np.float64)

        # density
        temp_array = []
        for num in file_csv[elem["name"]]:
            if num >= 0:
                temp_array.append(float(num))
        density_range = np.linspace(min_val, max_val, num_density_elements)
        try:
            density_temp = gaussian_kde(sorted(temp_array)).evaluate(density_range)
            by = float(density_range[1] - density_range[0])
            density = density_temp.tolist()
        except:
            by = 0
            density = []

        # tranform to percentage
        """
        x = sum(density)
        for i, c in enumerate(density):
            density[i] = density[i]/x
        """

    except:
        min_val = []
        max_val = []
        by = 0
        density = []

    # missings
    for i in file_csv[elem["name"]].unique():
        if i < 0:
            missings["frequencies"].append(
                file_csv[elem["name"]].value_counts()[i].astype(np.float64)
            )
            missings["values"].append(float(i))
            # missings["labels"].append.... # there are no labels for missings in numeric variables
    missing.append(sum(missings["frequencies"]))

    # total and valid
    total = int(file_csv[elem["name"]].size)
    valid = total - int(file_csv[elem["name"]].isnull().sum())

    number_dict = OrderedDict(
        [
            ("density", density),
            ("min", min_val),
            ("max", max_val),
            ("by", by),
            ("total", total),
            ("valid", valid),
            ("missing", missing),
            ("num_missings", missings),
        ]
    )

    return number_dict


def stats_cat(elem, file_csv):
    """Generate dict with statistics for categorical variables"""

    data_wm = file_csv[file_csv[elem["name"]] >= 0][elem["name"]]

    names = ["Median", "Valid", "Invalid"]
    values = []

    median = np.median(data_wm)

    total = int(file_csv[elem["name"]].size)
    valid = total - int(file_csv[elem["name"]].isnull().sum())
    invalid = int(file_csv[elem["name"]].isnull().sum())

    value_names = [median, valid, invalid]

    for v in value_names:
        values.append(str(v))

    statistics = OrderedDict([("names", names), ("values", values)])

    return statistics
    

def stats_string(elem, file_csv):
    """Generate dict with statistics for nominal variables"""

    names = ["Valid", "Invalid"]
    values = []

    total = int(file_csv[elem["name"]].size)
    valid = int(file_csv[elem["name"]].value_counts().sum())
    invalid = int(file_csv[elem["name"]].isnull().sum())
    for i in file_csv[elem["name"]]:
        if i == "" or i == ".":
            valid = valid - 1
            invalid = invalid + 1

    value_names = [valid, invalid]

    for v in value_names:
        values.append(str(v))

    statistics = OrderedDict([("names", names), ("values", values)])

    return statistics
    

def stats_number(elem, file_csv):
    """Generate dict with statistics for numerical variables"""

    data_wm = file_csv[file_csv[elem["name"]] >= 0][elem["name"]]

    names = ["Min.", "1st Qu.", "Median", "Mean", "3rd Qu.", "Max.", "Valid", "Invalid"]
    values = []

    min_val = min(data_wm)
    max_val = max(data_wm)

    median = np.median(data_wm)
    mean = np.mean(data_wm)

    mid = int(len(sorted(data_wm)) / 2)
    first_q = np.median(sorted(data_wm)[:mid])
    if len(sorted(data_wm)) % 2 == 0:
        third_q = np.median(sorted(data_wm)[mid:])
    else:
        third_q = np.median(sorted(data_wm)[mid + 1 :])

    total = int(file_csv[elem["name"]].size)
    valid = total - int(file_csv[elem["name"]].isnull().sum())
    invalid = int(file_csv[elem["name"]].isnull().sum())

    value_names = [min_val, first_q, median, mean, third_q, max_val, valid, invalid]

    for v in value_names:
        values.append(str(v))

    statistics = OrderedDict([("names", names), ("values", values)])

    return statistics


def uni_statistics(elem, file_csv):
    """Call function to generate statistics depending on the variable type"""

    if elem["type"] == "cat":

        statistics = stats_cat(elem, file_csv)

    elif elem["type"] == "string":

        statistics = stats_string(elem, file_csv)

    elif elem["type"] == "number":

        statistics = stats_number(elem, file_csv)

    return statistics


def uni(elem, elem_de, file_csv):
    """Call function to generate frequencies depending on the variable type"""

    statistics = OrderedDict()

    if elem["type"] == "cat":
        cat_dict = uni_cat(elem, elem_de, file_csv)

        statistics.update(cat_dict)

    elif elem["type"] == "string":

        string_dict = uni_string(elem, file_csv)

        statistics.update(string_dict)

    elif elem["type"] == "number":

        number_dict = uni_number(elem, file_csv)

        statistics.update(number_dict)

    return statistics
    

def stat_dict(
    elem,
    elem_de,
    file_csv,
    file_json,
    file_de_json,
    analysis_unit,
    period,
    sub_type,
    study
):
    """Fill variables with metadata of the dataset."""
    
    scale = elem["type"][0:3]

    if type(sub_type) == np.float64 and math.isnan(sub_type) == True:
        sub_type = ""

    stat_dict = OrderedDict()

    try:
        stat_dict["study"] = file_json["study"]
    except:
        stat_dict["study"] = study
    try:
        stat_dict["analysis_unit"] = file_json["analysis_unit"]
    except:
        stat_dict["analysis_unit"] = analysis_unit
    try:
        stat_dict["period"] = file_json["period"]
    except:
        stat_dict["period"] = str(period)
    try:
        stat_dict["conceptual_dataset"] = file_json["conceptual_dataset"]
    except:
        pass
    try:
        stat_dict["sub_type"] = file_json["sub_type"]
    except:
        stat_dict["sub_type"] = sub_type
    try:
        stat_dict["boost"] = file_json["boost"]
    except:
        pass
    stat_dict["dataset"] = file_json["name"].lower()
    stat_dict["dataset_cs"] = file_json["name"]
    stat_dict["variable"] = elem["name"]
    stat_dict["name"] = elem["name"].lower()
    stat_dict["name_cs"] = elem["name"]
    stat_dict["label"] = elem["label"]
    stat_dict["scale"] = scale
    stat_dict["uni"] = uni(elem, elem_de, file_csv)

    # For 10 or less values the statistics aren't shown.

    if elem["type"] == "number" or elem["type"] == "cat":
        data_wm = file_csv[file_csv[elem["name"]] >= 0][elem["name"]]
        if sum(Counter(data_wm.values).values()) > 10:
            stat_dict["statistics"] = uni_statistics(elem, file_csv)
    else:
        stat_dict["statistics"] = uni_statistics(elem, file_csv)

    if elem_de != "":
        stat_dict["label_de"] = elem_de["label"]

    return stat_dict


def generate_stat(
    data,
    metadata,
    metadata_de,
    analysis_unit,
    period,
    sub_type,
    study
):
    """Prepare statistics for every variable"""

    stat = []
    if metadata_de != "":
        elements = zip(
            metadata["resources"][0]["schema"]["fields"],
            metadata_de["resources"][0]["schema"]["fields"],
        )
    else:
        elements = list()
        for elem in metadata["resources"][0]["schema"]["fields"]:
            elements.append((elem, ""))
    for elem, elem_de in elements:
        try:
            stat.append(
                stat_dict(
                    elem,
                    elem_de,
                    data,
                    metadata,
                    metadata_de,
                    analysis_unit,
                    period,
                    sub_type,
                    study
                )
            )
        except:
            pass
    return stat




def write_json(
    data,
    metadata,
    filename,
    analysis_unit="",
    period="",
    sub_type="",
    study="",
    metadata_de=""
):
    stat = generate_stat(
        data,
        metadata,
        metadata_de,
        analysis_unit,
        period,
        sub_type,
        study
    )
    
    print('write "' + filename + '"')
    with open(filename, "w") as json_file:
        json.dump(stat, json_file, indent=2)
