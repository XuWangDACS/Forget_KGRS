from rdflib import Variable, Namespace, Graph
from rdflib_hdt import HDTStore, optimize_sparql
from forget_functions import *
from tqdm import tqdm
import networkx as nx

optimize_sparql()

relation_list_nowatch = {'starring', 'produced_by_producer', 'directed_by', 'edited_by', 'cinematography', 'wrote_by', 'belong_to', 'produced_by_company'}

graph = Graph(store=HDTStore("forget_data/Knowledge_Graph_without_Review.hdt"))
ex = Namespace("http://example.org/")

G = Graph()

general_rules = []

with open("forget_data/general_rules_wo_watch.txt", "r") as file:
    for line in file:
        general_rules.append(line.strip())
        
for rule in general_rules:
    body = rule.split(" <= ")[1]
    atoms = body.split(" & ")
    where_query = ""
    for atom in atoms:
        s, p, o = get_s_p_o(atom)
        where_query += f"?{s} ex:{p} ?{o} . \n"
    query = f"PREFIX ex: <http://example.org/>\n SELECT ?A ?B WHERE {{ {where_query} FILter (?A != ?B) \n }}"
    qres = graph.query(query)
    for row in qres:
        G.add((row.A, ex["recommend"], row.B))

G.serialize("forget_data/general_rules_KG.nt", format="nt")