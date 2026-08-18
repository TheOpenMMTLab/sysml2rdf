from rdflib import Graph, URIRef, RDFS
from py_traceability_rdf import Traceability
from obse.graphwrapper import GraphWrapper
from .sysml_collector import SysMLCollector


def create_design_element(wrapper, design_element):
    if "traceability_id" not in design_element:
        return
    rdf_id = wrapper.add_labeled_instance(Traceability.DesignElement, design_element["name"], design_element['traceability_id'])

    if "traceability_ref" in design_element:
        for ref in design_element["traceability_ref"]:
            rdf_ref = wrapper.create_ref(Traceability.Requirement, ref)
            wrapper.add_reference(Traceability.satisfies, rdf_id, rdf_ref)

def create_traceability_rdf_model(collector: SysMLCollector):
    # Create RDF model
    graph = Graph()

    # Bind a user-declared namespace to a prefix
    graph.bind("trc", Traceability)

    wrapper = GraphWrapper(graph, "http://frittenburger.de/sysml2rdf")

    # Add DesignElements and References to Requierments and Implemenations
    for clazz_id, clazz in collector.clazzes().items():
        create_design_element(wrapper, clazz)
     
    for use_case_id, use_case in collector.use_cases().items():
        create_design_element(wrapper, use_case)

    return graph
