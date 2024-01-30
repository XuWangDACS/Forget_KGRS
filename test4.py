import rdflib
import pandas as pd

g = rdflib.Graph()
g.parse("exp_data/KnowlegeGraph.ttl", format="turtle")

g.serialize(destination='exp_data/KnowlegeGraph.nt', format='nt')