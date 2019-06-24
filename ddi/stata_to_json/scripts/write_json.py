"""write_json.py"""
__author__ = "Marius Pahl"

import json
import math
from collections import Counter, OrderedDict

import numpy as np


def uni_cat(elem, elem_de, file_csv):
    """Generate dict with frequencies and labels for categorical variables

    Input:
    elem: dict
    elem_de: dict or string if there is no second language ("")
    file_csv: pandas DataFrame

    Output:
    cat_dict: OrderedDict
    """

    frequencies = []
    values = []
    missings = []
    labels = []

    stata_missings = {
        "4294967287": "-9",
        "4294967288": "-8",
        "4294967289": "-7",
        "4294967290": "-6",
        "4294967291": "-5",
        "4294967292": "-4",
        "4294967293": "-3",
        "4294967294": "-2",
        "4294967295": "-1",
    }

    if elem_de != "":
        labels_de = []

        value_count = file_csv[elem["name"]].value_counts()
        for (value, value_de) in zip(elem["values"], elem_de["values"]):
            try:
                frequencies.append(int(value_count[value["value"]]))
            except:
                frequencies.append(0)
            labels.append(value["label"])
            labels_de.append(value_de["label"])

            var_value = str(value["value"])

            if int(var_value) >= 0 and var_value not in stata_missings:
                missings.append("false")
                values.append(var_value)
            else:
                missings.append("true")
                if var_value in stata_missings:
                    values.append(stata_missings[var_value])
                else:
                    values.append(var_value)
    else:
        value_count = file_csv[elem["name"]].value_counts()
        for value in elem["values"]:
            try:
                frequencies.append(int(value_count[value["value"]]))
            except:
                frequencies.append(0)
            labels.append(value["label"])

            var_value = str(value["value"])

            if int(value["value"]) >= 0 and var_value not in stata_missings:
                missings.append("false")
                values.append(var_value)
            else:
                missings.append("true")
                if var_value in stata_missings:
                    values.append(stata_missings[var_value])
                else:
                    values.append(var_value)

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


def uni_string():
    """Generate dict with frequencies for nominal variables

    Output:
    string_dict: OrderedDict
    """

    string_dict = OrderedDict()

    string_dict["frequencies"] = []
    string_dict["labels"] = []
    string_dict["missings"] = []
    string_dict["values"] = []
    string_dict["labels_de"] = []

    return string_dict


def uni_number():
    """Generate dict with frequencies for numerical variables

    Input:
    elem: dict
    file_csv: pandas DataFrame
    num_density_elements: int (number of steps for density calculations; not now implemented)

    Output:
    number_dict: OrderedDict
    """
    number_dict = OrderedDict()

    number_dict["frequencies"] = []
    number_dict["labels"] = []
    number_dict["missings"] = []
    number_dict["values"] = []
    number_dict["labels_de"] = []

    return number_dict


def stats_cat(elem, file_csv):
    """Generate dict with statistics for categorical variables

    Input:
    elem: dict
    file_csv: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    names = ["valid", "invalid"]
    values = []

    total = int(file_csv[elem["name"]].size)
    invalid = int(file_csv[elem["name"]].isnull().sum()) + int(
        sum(n < 0 for n in file_csv[elem["name"]])
    )
    valid = total - invalid

    value_names = [valid, invalid]

    for value_name in value_names:
        values.append(str(value_name))

    statistics = OrderedDict([("names", names), ("values", values)])

    return statistics


def stats_string(elem, file_csv):
    """Generate dict with statistics for nominal variables

    Input:
    elem: dict
    file_csv: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    names = ["valid", "invalid"]
    values = []

    int(file_csv[elem["name"]].size)
    valid = int(file_csv[elem["name"]].value_counts().sum())
    invalid = int(file_csv[elem["name"]].isnull().sum())
    for i in file_csv[elem["name"]]:
        if i in ("", "."):
            valid = valid - 1
            invalid = invalid + 1

    value_names = [valid, invalid]

    for value_name in value_names:
        values.append(str(value_name))

    statistics = OrderedDict([("names", names), ("values", values)])

    return statistics


def stats_number(elem, file_csv):
    """Generate dict with statistics for numerical variables

    Input:
    elem: dict
    file_csv: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    data_wm = file_csv[file_csv[elem["name"]] >= 0][elem["name"]]

    names = ["Min.", "1st Qu.", "Median", "Mean",
             "3rd Qu.", "Max.", "valid", "invalid"]
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
        third_q = np.median(sorted(data_wm)[mid + 1:])

    total = int(file_csv[elem["name"]].size)
    invalid = int(file_csv[elem["name"]].isnull().sum()) + int(
        sum(n < 0 for n in file_csv[elem["name"]])
    )
    valid = total - invalid

    value_names = [min_val, first_q, median,
                   mean, third_q, max_val, valid, invalid]

    for value_name in value_names:
        values.append(str(value_name))

    statistics = OrderedDict([("names", names), ("values", values)])

    return statistics


def uni_statistics(elem, file_csv):
    """Call function to generate statistics depending on the variable type

    Input:
    elem: dict
    file_csv: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    if elem["type"] == "cat":

        statistics = stats_cat(elem, file_csv)

    elif elem["type"] == "string":

        statistics = stats_string(elem, file_csv)

    elif elem["type"] == "number":

        statistics = stats_number(elem, file_csv)

    else:
        statistics = dict()

    return statistics


def uni(elem, elem_de, file_csv):
    """Call function to generate frequencies depending on the variable type

    Input:
    elem: dict
    elem_de: dict or string if there is no second language ("")
    file_csv: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    statistics = OrderedDict()

    if elem["type"] == "cat":
        cat_dict = uni_cat(elem, elem_de, file_csv)

        statistics.update(cat_dict)

    elif elem["type"] == "string":

        string_dict = uni_string()

        statistics.update(string_dict)

    elif elem["type"] == "number":

        number_dict = uni_number()

        statistics.update(number_dict)

    else:
        pass

    return statistics


def stat_dict(
    elem,
    elem_de,
    file_csv,
    file_json,
    analysis_unit,
    period,
    sub_type,
    boost,
    study,
):
    """Fill variables with metadata of the dataset.

    Input:
    elem: dict
    elem_de: dict or string if there is no second language ("")
    file_csv: pandas DataFrame
    file_json: dict
    analysis_unit: string
    period: string
    sub_type: string
    boost: int
    study: string

    Output:
    meta_dict: OrderedDict
    """

    scale = elem["type"][0:3]

    if isinstance(sub_type, np.float64) and math.isnan(sub_type) == True:
        sub_type = ""

    meta_dict = OrderedDict()

    meta_dict["study"] = study
    meta_dict["analysis_unit"] = analysis_unit
    meta_dict["period"] = str(period)
    meta_dict["sub_type"] = sub_type
    meta_dict["boost"] = boost
    meta_dict["dataset"] = file_json["name"].lower()
    meta_dict["variable"] = elem["name"].lower()
    meta_dict["name"] = elem["name"].lower()
    meta_dict["name_cs"] = elem["name"]
    meta_dict["label"] = elem["label"]
    meta_dict["scale"] = scale
    meta_dict["categories"] = uni(elem, elem_de, file_csv)

    # For 10 or less values the statistics aren't shown.

    if elem["type"] == "number" or elem["type"] == "cat":
        data_wm = file_csv[file_csv[elem["name"]] >= 0][elem["name"]]
        if sum(Counter(data_wm.values).values()) > 10:
            meta_dict["statistics"] = uni_statistics(elem, file_csv)
    else:
        meta_dict["statistics"] = uni_statistics(elem, file_csv)

    if elem_de != "":
        meta_dict["label_de"] = elem_de["label"]

    return meta_dict


def generate_stat(
    data, metadata, metadata_de, analysis_unit, period, sub_type, boost, study
):
    """Prepare statistics for every variable

    Input:
    data: pandas DataFrame (later called file_csv)
    metadata: dict (later called file_json)
    metadata_de: dict or string ("") (later called file_de_json)
    analysis_unit: string
    period: string
    sub_type: string
    boost: int
    study: string

    Output:
    stat: OrderedDict
    """

    stat = OrderedDict()
    if metadata_de != "":
        elements = zip(
            metadata["resources"][0]["schema"]["fields"],
            metadata_de["resources"][0]["schema"]["fields"],
        )
        elements_length = len(metadata["resources"][0]["schema"]["fields"])
    else:
        elements = list()
        for elem in metadata["resources"][0]["schema"]["fields"]:
            elements.append((elem, ""))
        elements_length = len(elements)
    i = 1
    for elem, elem_de in elements:
        print(str(i) + "/" + str(elements_length))
        i = i + 1
        varname = elem["name"].lower()
        try:
            stat[varname] = stat_dict(
                elem,
                elem_de,
                data,
                metadata,
                analysis_unit,
                period,
                sub_type,
                boost,
                study,
            )
        except Exception as exception:
            print(exception)

    return stat


def write_json(
    data,
    metadata,
    filename,
    analysis_unit="",
    period="",
    sub_type="",
    boost="",
    study="",
    metadata_de="",
):
    """Main function to write json.

    Input:
    data: pandas DataFrame (later called file_csv)
    metadata: dict (later called file_json)
    filename: string
    analysis_unit: string
    period: string
    sub_type: string
    boost: int or string if empty ("")
    study: string
    metadata_de: dict or string ("") (later called file_de_json)
    """

    stat = generate_stat(
        data, metadata, metadata_de, analysis_unit, period, sub_type, boost, study
    )

    print('write "' + filename + '"')
    with open(filename, "w") as json_file:
        json.dump(stat, json_file, indent=2)
