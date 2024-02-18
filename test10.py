import networkx as nx
from rdflib_hdt import HDTDocument
from rdflib import Namespace
from tqdm import tqdm

hdt = HDTDocument("forget_data/KnowlegeGraph.hdt")
ex = Namespace("http://example.org/")

relation_list_nowatch = {'starring', 'produced_by_producer', 'directed_by', 'edited_by', 'cinematography', 'wrote_by', 'belong_to', 'produced_by_company','watched'}

graph_dict = {}

for relation in tqdm(relation_list_nowatch,desc="Creating Graphs"):
    graph_dict[relation] = nx.DiGraph()
    triples,_  = hdt.search((None, ex[relation], None))
    for s,p,o in triples:
        graph_dict[relation].add_edge(s.replace("http://example.org/",""), o.replace("http://example.org/",""))

