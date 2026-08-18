import logging
import json
import re

import xml.etree.ElementTree as ET
from .sysml_collector import SysMLCollector

logger = logging.getLogger(__name__)


def handle_association(element, collector: SysMLCollector):
    # <packagedElement xmi:type="uml:Association" xmi:id="_Xi9cgJocEfGXyr6necwJmg" memberEnd="_Xi-qopocEfGXyr6necwJmg _Xi_RspocEfGXyr6necwJmg">
    #    <eAnnotations xmi:type="ecore:EAnnotation" xmi:id="_Xi-qoJocEfGXyr6necwJmg" source="org.eclipse.papyrus">
    #      <details xmi:type="ecore:EStringToStringMapEntry" xmi:id="_Xi-qoZocEfGXyr6necwJmg" key="nature" value="UML_Nature"/>
    #    </eAnnotations>
    #    <ownedEnd xmi:type="uml:Property" xmi:id="_Xi_RspocEfGXyr6necwJmg" name="feak" type="_2kwS4JoXEfGXyr6necwJmg" association="_Xi9cgJocEfGXyr6necwJmg"/>
    # </packagedElement>
    return False  # Todo ignore for a while


def set_class_type(element, collector: SysMLCollector):
    #  <Blocks:Block xmi:id="_nGfVcJoUEfGXyr6necwJmg" base_Class="_nF_mMJoUEfGXyr6necwJmg"/>
    base_class = element.get_attribute("base_Class")
    collector.set(base_class, "class_type", element.tag_name)
    return True

def set_port_type(element, collector: SysMLCollector):
    #  <Blocks:Block xmi:id="_nGfVcJoUEfGXyr6necwJmg" base_Class="_nF_mMJoUEfGXyr6necwJmg"/>
    base_class = element.get_attribute("base_Port")
    collector.set(base_class, "port_type", element.tag_name)
    return True

def redirect_to_xmi_type(element, collector: SysMLCollector):
    xmi_type = element.get_attribute("xmi:type")  # XMI-Typ
    element.set_key(xmi_type)
    handle(element, collector)  # Repeat
    return False  # Ignore


def set_name_and_type(element, collector: SysMLCollector):
    #  <packagedElement xmi:type="uml:Class" xmi:id="_nF_mMJoUEfGXyr6necwJmg" name="KME">

    xmi_id = element.get_attribute("xmi:id")  # XMI-ID
    name = element.get_attribute("name")  # Namen auslesen
    collector.set(xmi_id, "name", name)
    collector.set(xmi_id, "type", element.key)
    return True

def pass_through(element, collector: SysMLCollector):
    # This function does nothing and is used for elements that we want to ignore or pass through without processing.
    return True

def ignore(element, collector: SysMLCollector):
    # This function does nothing and ignores also childs
    return False  # Ignore

def parse_comment(comment: str) -> {}:
    """Parses a comment"""
    # Example comment:
    # Die Schnittstelle {id IF:KME:2:QKD:2-ABC} erfüllt 
    # die Anfroderungen {ref QKD:2, QKref-7, All:Req:Protokolle:Kompatibilität}

    metadata = {}

    # Detect invalid syntax: {id: ...} or {ref: ...} (colon after keyword)
    invalid_colon_pattern = r'\{(id|ref):\s*([^}]*)\}'
    if re.search(invalid_colon_pattern, comment):
        raise ValueError("Invalid syntax: use '{id ...}' or '{ref ...}' without colon after keyword")

    # Detect invalid syntax: space after opening brace e.g. { ref ...}
    invalid_space_pattern = r'\{\s+(id|ref)\s+([^}]*)\}'
    if re.search(invalid_space_pattern, comment):
        raise ValueError("Invalid syntax: no space allowed after opening brace")

    # Find all occurrences of {id ...} and {ref ...}
    pattern = r'\{(id|ref)\s+([^}]+)\}'
    for match in re.finditer(pattern, comment):
        kind = match.group(1)
        uids_str = match.group(2)

        # Validate: UIDs must be comma-separated, no spaces within uid list without commas
        uids = [u.strip() for u in uids_str.split(",")]
        for uid in uids:
            if ' ' in uid:
                raise ValueError(f"Invalid syntax: UIDs must be comma-separated, found space in '{uid}'")

        if kind == "id":
            # id must be exactly one UID
            if len(uids) != 1:
                raise ValueError("Invalid syntax: {id ...} must contain exactly one UID")
            metadata["id"] = uids[0]
        else:
            if "ref" in metadata:
                metadata["ref"].extend(uids)
            else:
                metadata["ref"] = uids

    return metadata
    

def handle_comment(element, collector: SysMLCollector):
    #  <packagedElement xmi:type="uml:Association" xmi:id="_Na8kILlTEfCy4YdqQT5Wvw" name="IF-KME-2-QKD-2" memberEnd="_Na9LMrlTEfCy4YdqQT5Wvw _Na9yQLlTEfCy4YdqQT5Wvw">
    # <ownedComment xmi:type="uml:Comment" xmi:id="_hhsEAFKJEfCGt4EH7VyqHw" annotatedElement="_hhw8gFKJEfCGt4EH7VyqHw">
    #   <body>Exchange data securely</body>
    # </ownedComment>
    comment_for_id = element.parent.parent.get_attribute("xmi:id")
    comment_body = element.text  # is UTF-8 encoded text

    # parse comment
    metadata = parse_comment(comment_body)
   
    for key , values in metadata.items():
        if type(values) == str:
            collector.set(comment_for_id, f"traceability_{key}", values)
        else:
            for value in values:
                collector.append(comment_for_id, f"traceability_{key}", value)
        
    collector.append(comment_for_id, "comment", comment_body)
    return True

def handle_port(element, collector: SysMLCollector):
    # <ownedAttribute xmi:type="uml:Port" xmi:id="_zlMwgJoiEfGcv5eHsjSnuQ" name="etsi014_app" visibility="public" type="_rIuv8JohEfGcv5eHsjSnuQ" aggregation="composite"/>
    port_for_id = element.parent.get_attribute("xmi:id")
    port_name = element.get_attribute("name")
    port_type = element.get_attribute("type")

    collector.append(port_for_id, "port", {"name": port_name, "type": port_type})
    return True


def handle_property(element, collector: SysMLCollector):
    # <ownedAttribute xmi:type="uml:Property" xmi:id="_EoTMgpogEfGcv5eHsjSnuQ" name="qkd" type="_YisC4JoWEfGXyr6necwJmg" aggregation="composite" association="_EoSlcJogEfGcv5eHsjSnuQ"/>
    property_for_id = element.parent.get_attribute("xmi:id")
    property_name = element.get_attribute("name")
    print(f"Property {property_name}")

    property_type = element.get_attribute("type")
    # property_association = element.get_attribute("association") nicht immer, z.B. stw in System Digitaler Befehl
    # TODO handle property
    return True

handlers = {
    "xmi:XMI": pass_through,
    "uml:Model": pass_through,
    "packagedElement": redirect_to_xmi_type,
    "packageImport": ignore,
    "profileApplication": ignore,


    "uml:UseCase": set_name_and_type,
    "uml:Actor": set_name_and_type,

    "uml:Package": pass_through,
    "uml:Class": set_name_and_type,
    "uml:Port": handle_port,
    "ownedComment": pass_through,
    "ownedAttribute": redirect_to_xmi_type,
    "body": handle_comment,
    "uml:Property": handle_property,

    "ownedConnector": ignore, # TODO wird erstmal ignoriert
    "Blocks:NestedConnectorEnd": ignore, # TODO wird erstmal ignoriert
    "Blocks:BindingConnector": ignore, # TODO wird erstmal ignoriert

    "lowerValue": ignore, # TODO wird erstmal ignoriert, lower Value multiplicity
    "upperValue": ignore, # TODO wird erstmal ignoriert, upper Value 
    
    "Blocks:Block":  set_class_type,
    "PortsAndFlows:InterfaceBlock":  set_class_type,
    "PortsAndFlows:ProxyPort": set_port_type,

    "uml:Association": handle_association,
}


def handle(element, collector):

    if element.key in handlers:
        if not handlers[element.key](element, collector):
            return  # Stop loop
    else:
        print(f"No handler for {element.key}, Tag: {element.tag_name} Attributes: {element.attributes}")

    # Recursively parse child elements
    for child in element.childs:
        handle(child, collector)  


class Wrapper:

    def _split(self, key, namespaces):
        """Splits an XML tag into its namespace and local name."""
        if '}' in key:
            namespace, local_name = key[1:].split('}', 1)
            namespace_key = namespaces[namespace]
            return namespace_key+":"+local_name
        else:
            return key

    def __init__(self, element, namespaces, parent = None):
        self.key = self.tag_name = self._split(element.tag, namespaces)
        self.parent = parent
        self.text = element.text

        # parse attributes
        self.attributes = {}
        for attr_name, attr_value in element.attrib.items():
            attr_key = self._split(attr_name, namespaces)  
            self.attributes[attr_key] = attr_value

        self.childs = []
        for child in element:
            self.childs.append(Wrapper(child, namespaces, self))

    def set_key(self, key):
        self.key = key

    def get_attribute(self, attr_key):
        if attr_key not in self.attributes:
            raise ValueError(f"No such key '{attr_key}' in {self.attributes}")
        return self.attributes[attr_key]

def get_namespace_map(filepath: str) -> dict[str, str]:
    """Extrahiert die Namespace-Prefix-zu-URI-Zuordnung aus dem Root-Element."""
    namespaces = {}
    for event, elem in ET.iterparse(filepath, events=["start-ns"]):
        prefix, uri = elem  # bei 'start-ns' ist elem ein (prefix, uri) Tuple
        namespaces[uri] = prefix
    return namespaces

def parse_sysml_file(file_path) -> SysMLCollector:
    """    Parses a SysML file and collects data about actors, use cases, subjects, associations, and requirements.
    Args:
        file_path (str): The path to the SysML file to be parsed.
    Returns:
        SysMLCollector: An instance of SysMLCollector containing the collected data.
    """
    logger.info(f"Parsing SysML file: {file_path}")

    ns = get_namespace_map(file_path)
    tree = ET.parse(file_path)
    root = tree.getroot()
    root_wrapper = Wrapper(root, ns)
    collector = SysMLCollector()

    handle(root_wrapper, collector)

    # Save json to file
    #with open('output.json', 'w') as f:
    #    json.dump(collector.dict_elements, f, indent=2)

    return collector

  