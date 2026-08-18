import argparse

from sysml2rdf.create_sysml_rdf_model import create_sysml_rdf_model
from sysml2rdf.create_traceability_rdf_model import create_traceability_rdf_model

from sysml2rdf.parse_sysml_file import parse_sysml_file


def parse_args():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='SysMP to RDF Transformation.')
    parser.add_argument("--input-sysml", required=True, help="Inputfile in SysML Format")
    parser.add_argument("--output-sysml-rdf", required=True, help="Outputfile SYSML-Model in RDF Format")
    parser.add_argument("--output-traceability-rdf", required=True, help="Outputfile Traceability-Model in RDF Format") 
    args = parser.parse_args()

    return args.input_sysml, args.output_sysml_rdf, args.output_traceability_rdf


input_sysml, output_sysml_rdf, output_traceability_rdf = parse_args()

sysml_collector = parse_sysml_file(input_sysml)

sysml_graph = create_sysml_rdf_model(sysml_collector)
sysml_graph.serialize(destination=output_sysml_rdf, format='turtle')

traceability_graph = create_traceability_rdf_model(sysml_collector)
traceability_graph.serialize(destination=output_traceability_rdf, format='turtle')


