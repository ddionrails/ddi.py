import glob, re, json, os
import yaml
from collections import OrderedDict
from lxml import etree

LANG_RE = re.compile(r'(\w{2})/[\w\d\-_]+.xml$', flags=re.IGNORECASE)

class Parser:

    def __init__(self, r2ddi_path="r2ddi", version=None, primary_language="en",
                 versions=["v1"], latest_version="v1"):
        """
        The ``version`` option is now DEPRECATED, pleas use the combination of
        ``versions`` (list) and ``latest_version`` from now on.
        """
        self.path = r2ddi_path
        self.versions = versions
        self.latest_version = latest_version

        # Temporary fix for the deprecated version option:
        if version:
            self.versions = [version]
            self.latest_version = version

        self.primary_language = primary_language
        self.datasets = OrderedDict()
        self.run()

    def run(self):
        primary_names = set(glob.glob(os.path.join(
            self.path, self.latest_version, self.primary_language, "*.xml",
        )))
        print(primary_names)
        secondary_names = set(glob.glob(os.path.join(
            self.path, self.latest_version, "*", "*.xml"
        ))).difference(primary_names)
        primary_names = sorted(primary_names)
        secondary_names = sorted(secondary_names)
        for file_name in primary_names:
            print("Read:", file_name)
            self._parse_xml_file(file_name)
        for file_name in secondary_names:
            print("Translate:", file_name)
            self._parse_xml_file(file_name, translate=True)

    def _parse_xml_file(self, path, translate=False):
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

    def _parse_xml_var(self, xml_var):
        dataset = xml_var.get("files").lower()
        variable = xml_var.get("ID").lower()
        var_dict = OrderedDict()
        var_dict["name"] = variable
        var_dict["name_cs"] = xml_var.get("ID")
        var_dict["variable"] = variable
        var_dict["dataset"] = dataset
        var_dict["label"] = xml_var.findtext("labl", default="")
        var_dict["categories"] = self._get_categories(xml_var)
        var_dict["statistics"] = self._get_statistics(xml_var)
        if xml_var.get("intrvl") == "labeled_numeric":
            var_dict["scale"] = "cat"
        else:
            var_dict["scale"] = ""
        if not dataset in self.datasets.keys():
            self.datasets[dataset] = OrderedDict()
        self.datasets[dataset][variable] = var_dict

    def _variable_translation(self, xml_var, language):
        dataset = xml_var.get("files").lower()
        variable = xml_var.get("ID").lower()
        label = "label_%s" % language
        labels = "labels_%s" % language
        self.datasets[dataset][variable][label] = xml_var.findtext("labl", default="")
        if len(xml_var.findall("catgry")) > 0:
            self.datasets[dataset][variable]["categories"][labels] = []
        for xml_cat in xml_var.findall("catgry"):
            self.datasets[dataset][variable]["categories"][labels].append(
                xml_cat.findtext("labl", default="")
            )

    def _get_categories(self, xml_var):
        result = OrderedDict()
        result["frequencies"] = []
        result["labels"] = []
        result["missings"] = []
        result["values"] = []
        for xml_cat in xml_var.findall("catgry"):
            try:
                result["frequencies"].append(int(xml_cat.findtext("catStat")))
            except:
                result["frequencies"].append(int(0))
            if xml_cat.get("missing", "").lower() == "true":
                result["missings"].append(True)
            else:
                result["missings"].append(False)
            value = xml_cat.findtext("catValu")
            result["values"].append(value)
            label = xml_cat.findtext("labl")
            if label:
                result["labels"].append(label)
            else:
                result["labels"].append(value)
        return result

    def _get_statistics(self, xml_var):
        result = OrderedDict()
        result["names"] = []
        result["values"] = []
        for xml_stat in xml_var.findall("sumStat"):
            result["names"].append(xml_stat.get("type"))
            result["values"].append(xml_stat.text)
        return result

    def write_json(self):
        os.system("rm -r ddionrails/datasets; mkdir -p ddionrails/datasets")
        for dataset_name, dataset in self.datasets.items():
            with open("ddionrails/datasets/%s.json" % dataset_name, "w") as f:
                json.dump(dataset, f, indent=2)

    def write_yaml(self):
        os.system("rm -r temp/datasets; mkdir -p temp/datasets")
        for dataset_name, dataset in self.datasets.items():
            with open("temp/datasets/%s.yaml" % dataset_name, "w") as f:
                yaml.dump(dataset, f, default_flow_style=False)
        
