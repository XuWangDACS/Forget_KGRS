from rdflib_hdt import HDTStore, optimize_sparql, HDTDocument
import networkx as nx

hdt = HDTDocument("forget_data/KnowlegeGraph.hdt")

triples, cardinality = hdt.search((None, None, None))
DiG = nx.DiGraph()
predicate_set = set()

for s, p, o in triples:
    sub = str(s).replace("http://example.org/","")
    pre = str(p).replace("http://example.org/","")
    obj = str(o).replace("http://example.org/","")
    predicate_set.add(pre)
    DiG.add_edge(sub,pre)
    DiG.add_edge(pre,obj)
    
degree_centrality = nx.degree_centrality(DiG)

predicate_degree_centrality = {node: centrality for node, centrality in degree_centrality.items() if node in predicate_set}

print(predicate_degree_centrality)