



python main.py --input-sysml ../../../workspace-papyrus/SQuIRRL/SQuIRRL.uml --output-sysml-rdf sysml.ttl --output-traceability-rdf traceability.ttl

# sysml_2_rdf("../../xmi-codegen/cleaned.xmi", "eulynx-test.ttl")
# sysml_2_rdf("../../xmi-codegen/EULYNX System BL4 v23 - BL4.xmi", "eulynx-test.ttl")
#python main.py --input-sysml ../../../xmi-codegen/cleaned.xmi --output-sysml-rdf sysml.ttl --output-traceability-rdf traceability.ttl


## Build docker image

```
docker build -t frittenburger/sysml2rdf:dev .
```