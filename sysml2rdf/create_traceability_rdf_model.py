from rdflib import Graph, URIRef, RDFS
from py_traceability_rdf import Traceability
from obse.graphwrapper import GraphWrapper
from .sysml_collector import SysMLCollector


def create_design_element(wrapper, design_element, designType):
    if "traceability_id" not in design_element:
        return
    rdf_id = wrapper.add_labeled_instance(Traceability.DesignElement, design_element["name"], design_element['traceability_id'])
    wrapper.add_str_property(Traceability.identifier, rdf_id, design_element["traceability_id"])
    wrapper.add_str_property(Traceability.designType, rdf_id, designType)

    if "traceability_ref" in design_element:
        for ref in design_element["traceability_ref"]:
            rdf_ref = wrapper.create_ref(Traceability.Requirement, ref)
            wrapper.add_reference(Traceability.satisfies, rdf_id, rdf_ref)

    if "comment" in design_element:
        wrapper.add_comment(rdf_id, "\n".join(design_element["comment"]))


def create_traceability_rdf_model(collector: SysMLCollector):
    # Create RDF model
    graph = Graph()

    # Bind a user-declared namespace to a prefix
    graph.bind("trc", Traceability)

    wrapper = GraphWrapper(graph, "https://osm.hpi.de/2026/08/SQuIRRL")

    # Add DesignElements and References to Requierments and Implemenations
    for clazz_id, clazz in collector.clazzes().items():
        create_design_element(wrapper, clazz, clazz["class_type"])
     
    for use_case_id, use_case in collector.use_cases().items():
        create_design_element(wrapper, use_case, "uml:UseCase")

    return graph
