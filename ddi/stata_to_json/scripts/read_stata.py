import logging
import re

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def cat_values(var, varscale, df_data, data):

    cat_dict = []

    """
    old imports of negative values:
    2^32-3 = 4294967293 == [-3] nicht valide
    2^32-2 = 4294967294 == [-2] trifft nicht zu
    2^32-1 = 4294967295 == [-1] keine Angabe
    """
    df_nomis = df_data[var].copy()

    for index, value in enumerate(df_nomis):
        if isinstance(value, str) == False and value < 0:
            df_nomis[index] = np.nan

    label_dict = data.value_labels()

    for sn, label in enumerate(data.lbllist):
        if label == varscale["name"]:
            value_list = label
            value_labels = label_dict[label]

    for v, l in value_labels.items():
        cat_dict.append(dict(value=int(v), label=l))

    return cat_dict


def scale_var(var, varscale, df_data):
    if varscale["name"] != "":
        return "cat"
    var_type = str(df_data[var].dtype)
    match_float = re.search("float\d*", var_type)
    match_int = re.search("int\d*", var_type)
    if match_float or match_int:
        var_type = "number"
    if var_type == "object":
        var_type = "string"
    return var_type


def generate_tdp(vars, varlabels, varscale, dta_file, df_data, data):
    dataset_name = re.sub(".dta", "", dta_file)

    tdp = {}
    fields = []

    for var, varscale in zip(vars, varscale):
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

    # transform StataReader Object
    d = data.read()

    # vars = [dict(name=var, sn=sn) for sn, var in enumerate(data.varlist) ]
    vars = data.varlist

    # Import
    # varlabels = [dict(name=data.variable_labels()[varlabel], sn=sn) for sn, varlabel in enumerate(data.variable_labels()) ]
    varlabels = data.variable_labels()

    varscale = [dict(name=varscale, sn=sn) for sn, varscale in enumerate(data.lbllist)]
    # varvalues = data.value_labels()

    dta_file = re.search("^.*\/(.*)", stata_name).group(1)
    m = generate_tdp(vars, varlabels, varscale, dta_file, d, data)

    return d, m


def read_stata(stata_name):
    logger.info('read "' + stata_name + '"')
    data = pd.read_stata(stata_name, iterator=True, convert_categoricals=False)
    d, m = parse_dataset(data, stata_name)
    return d, m
