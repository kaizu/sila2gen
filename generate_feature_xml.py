# -*- coding: utf-8 -*-

import pathlib
from xml.dom import minidom
import xml.etree.ElementTree as ET
import yaml


def set_identifier(element, doc):
    ET.SubElement(element, "Identifier").text = doc["Identifier"]
    ET.SubElement(element, "DisplayName").text = doc.get("DisplayName", doc["Identifier"])
    ET.SubElement(element, "Description").text = doc.get("Description", doc["Identifier"])

def set_observable(element, doc):
    if "Observable" not in doc:
        ET.SubElement(element, "Observable").text = "No"
    else:
        value = doc["Observable"]
        if isinstance(value, str):
            ET.SubElement(element, "Observable").text = value
        elif isinstance(value, bool):
            ET.SubElement(element, "Observable").text = "Yes" if value else "No"
        else:
            raise ValueError(f"The given Observable is invalid [{value}].")

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

    for c in doc["Command"]:
        command = ET.SubElement(root, "Command")
        set_identifier(command, c)
        set_observable(command, c)
        for p in c["Parameter"]:
            parameter = ET.SubElement(command, "Parameter")
            set_identifier(parameter, p)
            ET.SubElement(ET.SubElement(parameter, "DataType"), "Basic").text = p["DataType"]
        response = ET.SubElement(command, "Response")
        set_identifier(response, c["Response"])
        ET.SubElement(ET.SubElement(response, "DataType"), "Basic").text = c["Response"]["DataType"]

    for p in doc["Property"]:
        prop = ET.SubElement(root, "property")
        set_identifier(prop, p)
        set_observable(prop, p)
        ET.SubElement(ET.SubElement(prop, "DataType"), "Basic").text = p["DataType"]

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
        outputpath = pathlib.Path(workdir / f"{key}-v0.1.sila.xml")
        generate_yaml(outputpath, value)


if __name__ == "__main__":
    main("./features.yml", "artifacts")
