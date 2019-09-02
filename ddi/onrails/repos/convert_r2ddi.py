import glob
import json
import os
import re
from collections import OrderedDict
from typing import Dict

import pandas as pd
from lxml import etree

LANG_RE = re.compile(r"(\w{2})/[\w\d\-_]+.xml$", flags=re.IGNORECASE)


class Parser:
    def __init__(
        self,
        study_name,
        r2ddi_path="r2ddi",
        primary_language="en",
        versions=("v1",),
        latest_version="v1",
    ) -> None:
        self.study_name = study_name
        self.path = r2ddi_path
        self.versions = versions
        self.latest_version = latest_version
        self.primary_language = primary_language
        self.datasets = OrderedDict()
        self.run()

    def run(self) -> None:
        primary_names = set(
            glob.glob(
                os.path.join(
                    self.path, self.latest_version, self.primary_language, "*.xml"
                )
            )
        )
        secondary_names = set(
            glob.glob(os.path.join(self.path, self.latest_version, "*", "*.xml"))
        ).difference(primary_names)
        primary_names = sorted(primary_names)
        secondary_names = sorted(secondary_names)
        for file_name in primary_names:
            print("Read:", file_name)
            self._parse_xml_file(file_name)
        for file_name in secondary_names:
            print("Translate:", file_name)
            self._parse_xml_file(file_name, translate=True)

    def _parse_xml_file(self, path: str, translate: bool = False) -> None:
        xml_content = etree.parse(path)
        for xml_var in xml_content.findall("//var"):
            if translate:
                try:
                    language = LANG_RE.findall(path)[0]
                    self._variable_translation(xml_var, language)
                except:
                    print("[ERROR] Failed to parse translation for %s" % path)
            else:
                self._parse_xml_var(xml_var)

    def _parse_xml_var(self, xml_var: etree._Element) -> None:
        dataset = xml_var.get("files")
        variable = xml_var.get("ID")
        var_dict = OrderedDict()
        var_dict["study"] = self.study_name
        var_dict["dataset"] = dataset
        var_dict["name"] = variable
        var_dict["label"] = xml_var.findtext("labl", default="")
        var_dict["categories"] = self._get_categories(xml_var)
        var_dict["statistics"] = self._get_statistics(xml_var)
        if xml_var.get("intrvl") == "labeled_numeric":
            var_dict["scale"] = "cat"
        else:
            var_dict["scale"] = ""
        if dataset not in self.datasets:
            self.datasets[dataset] = {}
        self.datasets[dataset][variable] = var_dict

    def _variable_translation(self, xml_var: etree._Element, language: str) -> None:
        dataset = xml_var.get("files")
        variable = xml_var.get("ID")
        label = f"label_{language}"
        labels = f"labels_{language}"
        self.datasets[dataset][variable][label] = xml_var.findtext("labl", default="")
        self.datasets[dataset][variable]["categories"][labels] = self._get_categories(
            xml_var
        )["labels"]

    def _get_categories(self, xml_var: etree._Element) -> Dict:
        frequencies = []
        labels = []
        missings = []
        values = []
        int_cats = []
        str_cats = []
        for xml_cat in xml_var.findall("catgry"):
            value = xml_cat.findtext("catValu")
            try:
                v = int(value)
                int_cats.append((v, xml_cat))
            except:
                str_cats.append((value, xml_cat))
        xml_cats = [
            x[1]
            for x in sorted(int_cats, key=lambda x: x[0])
            + sorted(str_cats, key=lambda x: x[0])
        ]
        for xml_cat in xml_cats:
            try:
                cat_stat = int(xml_cat.findtext("catStat"))
            except:
                cat_stat = 0
            frequencies.append(cat_stat)
            if xml_cat.get("missing", "").lower() == "true":
                missings.append(True)
            else:
                missings.append(False)
            value = xml_cat.findtext("catValu").strip()
            values.append(value)
            label = xml_cat.findtext("labl")
            if label:
                labels.append(label)
            else:
                labels.append(value)

        # use pandas to sort those lists based on "values"
        sorting_dataframe = pd.DataFrame(
            {
                "values": values,
                "labels": labels,
                "missings": missings,
                "frequencies": frequencies,
            }
        )
        sorting_dataframe["labels"] = sorting_dataframe["labels"].astype(str)
        sorting_dataframe["values"] = pd.to_numeric(sorting_dataframe["values"])
        sorting_dataframe.sort_values(by="values", inplace=True)
        return sorting_dataframe.to_dict("list")

    def _get_statistics(self, xml_var: etree._Element) -> OrderedDict:
        statistics = OrderedDict()
        for xml_stat in xml_var.findall("sumStat"):
            _type = xml_stat.get("type")
            value = xml_stat.text.strip()
            if value in ("NA", "NaN"):
                value = None
            # float or scientific notation, e.g. 1e+05
            elif "." in value or "+" in value:
                value = float(value)
            else:
                value = int(value)
            statistics[_type] = value
        return statistics

    def write_json(self) -> None:
        os.system("rm -r ddionrails/datasets; mkdir -p ddionrails/datasets")
        for dataset_name, dataset in self.datasets.items():
            with open(f"ddionrails/datasets/{dataset_name}.json", "w") as outfile:
                json.dump(list(dataset.values()), outfile, indent=2)
