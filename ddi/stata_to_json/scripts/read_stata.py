"""read_stata.py"""
__author__ = "Marius Pahl"

import logging
import re

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)


def cat_values(var, varscale, df_data, data):
    '''
    Extrat categorical metadata from stata files

    Input:
    var: string
    varscale: dict
    df_data: pandas DataFrame
    data: pandas StataReader

    Output:
    cat_list: list
    '''

    cat_list = list()

    df_nomis = df_data[var].copy()

    for index, value in enumerate(df_nomis):
        if isinstance(value, str) == False and value < 0:
            df_nomis[index] = np.nan

    label_dict = data.value_labels()

    for label in data.lbllist:
        if label == varscale["name"]:
            value_labels = label_dict[label]

    for value, label in value_labels.items():
        cat_list.append(dict(value=int(value), label=label))

    return cat_list


def scale_var(var, varscale, df_data):
    '''
    Select vartype

    Input:
    var: string
    varscale: dict
    df_data: pandas DataFrame

    Output:
    var_type: string
    '''

    if varscale["name"] != "":
        return "cat"
    var_type = str(df_data[var].dtype)
    match_float = re.search(r"float\d*", var_type)
    match_int = re.search(r"int\d*", var_type)
    if match_float or match_int:
        var_type = "number"
    if var_type == "object":
        var_type = "string"
    return var_type


def generate_tdp(vars, varlabels, varscales, dta_file, df_data, data):
    '''
    Generate tabular data package file

    Input:
    vars: list
    varlabels: dict
    varscale: list
    dta_file: string
    df_data: pandas DataFrame
    data: pandas StataReader

    Output:
    tdp: dict
    '''

    dataset_name = re.sub(".dta", "", dta_file)

    tdp = {}
    fields = []

    for var, varscale in zip(vars, varscales):
        scale = scale_var(var, varscale, df_data)
        meta = dict(name=var, label=varlabels[var], type=scale)
        if scale == "cat":
            meta["values"] = cat_values(var, varscale, df_data, data)

        fields.append(meta)

    schema = {}

    schema.update(fields=fields)

    resources = []

    resources.append(dict(path=dta_file, schema=schema))

    tdp.update(dict(name=dataset_name, resources=resources))

    return tdp


def parse_dataset(data, stata_name):
    '''
    Create data and metadata

    Input:
    data: pandas StataReader
    stata_name: string

    Output:
    datatable: pandas DataFrame
    metadata: dict
    '''

    datatable = data.read()

    vars = data.varlist

    varlabels = data.variable_labels()

    varscales = [dict(name=varscale, sn=number)
                for number, varscale in enumerate(data.lbllist)]

    dta_file = re.search(r"^.*\/(.*)", stata_name).group(1)
    metadata = generate_tdp(vars, varlabels, varscales, dta_file, datatable, data)

    return datatable, metadata


def read_stata(stata_name):
    '''
    Read stata files (dta)

    Input:
    stata_name: string

    Output:
    datatable: pandas DataFrame
    metadata: dict
    '''

    print('read "' + stata_name + '"')
    data = pd.read_stata(stata_name, iterator=True, convert_categoricals=False)
    datatable, metadata = parse_dataset(data, stata_name)

    return datatable, metadata
