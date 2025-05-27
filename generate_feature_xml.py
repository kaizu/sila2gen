# -*- coding: utf-8 -*-

import pathlib
import subprocess
from xml.dom import minidom
import xml.etree.ElementTree as ET
import yaml


def getchain(doc, keys, default=None, exist=False):
    for key in keys:
        if key in doc:
            return doc[key]
    else:
        if exist:
            raise KeyError(f"{keys}")
    return default

def set_identifier(element, doc):
    ET.SubElement(element, "Identifier").text = getchain(doc, ("Identifier", "id"), exist=True)
    ET.SubElement(element, "DisplayName").text = getchain(doc, ("DisplayName", "Identifier", "id"), exist=True)
    ET.SubElement(element, "Description").text = getchain(doc, ("Description", "Identifier", "id"), exist=True)

def set_observable(element, doc):
    value = getchain(doc, ("Observable", "observable"), default=None)
    if value is None:
        ET.SubElement(element, "Observable").text = "No"
    else:
        if isinstance(value, str):
            ET.SubElement(element, "Observable").text = value
        elif isinstance(value, bool):
            ET.SubElement(element, "Observable").text = "Yes" if value else "No"
        else:
            raise ValueError(f"The given Observable is invalid [{value}].")

def _set_datatype(element, value):
    if isinstance(value, str):
        assert value in ("String", "Integer", "Boolean"), value
        ET.SubElement(ET.SubElement(element, "DataType"), "Basic").text = value
    elif isinstance(value, list):
        assert len(value) == 1, value
        _set_datatype(ET.SubElement(ET.SubElement(element, "DataType"), "List"), value[0])
    elif isinstance(value, dict):
        structure = ET.SubElement(ET.SubElement(element, "DataType"), "Structure")
        for k, v in value.items():
            assert isinstance(k, str), k
            elem = ET.SubElement(structure, "Element")
            ET.SubElement(elem, "Identifier").text = k
            ET.SubElement(elem, "DisplayName").text = k
            ET.SubElement(elem, "Description").text = k
            _set_datatype(elem, v)
    else:
        raise ValueError(f"Unknown DataType given [{value}]")

def set_datatype(element, doc):
    _set_datatype(element, getchain(doc, ("DataType", "type"), exist=True))

def generate_yaml(outputpath, doc):
    root = ET.Element("Feature")

    root.set("xmlns", "http://www.sila-standard.org")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("Category", "examples")
    root.set("FeatureVersion", "1.0")
    root.set("MaturityLevel", "Verified")
    root.set("Originator", "org.silastandard")
    root.set("SiLA2Version", "1.0")
    root.set("xsi:schemaLocation", "http://www.sila-standard.org https://gitlab.com/SiLA2/sila_base/raw/master/schema/FeatureDefinition.xsd")

    set_identifier(root, doc)

    for c in getchain(doc, ("Command", "commands"), default=()):
        command = ET.SubElement(root, "Command")
        set_identifier(command, c)
        set_observable(command, c)
        for p in getchain(c, ("Parameter", "parameters"), default=()):
            parameter = ET.SubElement(command, "Parameter")
            set_identifier(parameter, p)
            set_datatype(parameter, p)
        for r in getchain(c, ("Response", "responses"), exist=True):
            response = ET.SubElement(command, "Response")
            set_identifier(response, r)
            set_datatype(response, r)

    for p in getchain(doc, ("Property", "properties"), default=()):
        prop = ET.SubElement(root, "Property")
        set_identifier(prop, p)
        set_observable(prop, p)
        set_datatype(prop, p)

    doc = minidom.parseString(ET.tostring(root, 'utf-8'))
    with outputpath.open("w") as f:
        doc.writexml(f, encoding='utf-8', newl='\n', indent='', addindent='  ')

def main(filename, workdirname="."):
    filepath = pathlib.Path(filename)
    assert filepath.is_file(), filepath
    workdir = pathlib.Path(workdirname)
    if not workdir.exists():
        workdir.mkdir(parents=True)
    assert workdir.is_dir(), workdirname

    with filepath.open('r') as f:
        doc = yaml.safe_load(f)

    for key, value in doc.items():
        packagepath = workdir / f"{key}"
        if not packagepath.exists():
            packagepath.mkdir()

        outputpath = packagepath / f"{key}-v0.1.sila.xml"
        generate_yaml(outputpath, value)

        if not pathlib.Path(packagepath / f"{key}").exists():
            res = subprocess.run(
                f"cd {str(packagepath)} && sila2-codegen new-package --package-name {key} {outputpath.name}",
                shell=True, check=True)
        else:
            # Update the existing package. or overwrite by 'new-package' with '--overwrite' option
            res = subprocess.run(
                f"cd {str(packagepath)} && sila2-codegen update {outputpath.name}",
                shell=True, check=True)


if __name__ == "__main__":
    main("./features.yml", "./servers")
