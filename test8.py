from rdflib_hdt import HDTDocument
from rdflib import Variable, Namespace, Graph
from forget_functions import *
from tqdm import tqdm
import networkx as nx

hdt = HDTDocument("forget_data/Knowledge_Graph_without_Review.hdt")
ex = Namespace("http://example.org/")

graph = nx.Graph()

# relation_list = {'starring', 'produced_by_producer', 'directed_by', 'edited_by', 'cinematography', 'wrote_by', 'belong_to', 'produced_by_company'}

# for relation in tqdm(relation_list):
#     triples,_  = hdt.search((None, ex[relation], None))
#     for s,p,o in triples:
#         with open(f"forget_data/Knowledge_Graph_without_Review.nt", "a+") as file:
#             file.write(f"<{s}> <{p}> <{o}> .\n")

general_rules = []

with open("forget_data/general_rules_wo_watch.txt", "r") as file:
    for line in file:
        general_rules.append(line.strip())
        
for rule in tqdm(general_rules):
    query = []
    body = rule.split(" <= ")[1]
    atoms = body.split(" & ")
    tamplate = []
    var_dict = {}
    for atom in atoms:
        s, p, o = get_s_p_o(atom)
        if s not in var_dict:
            var_dict[s] = Variable(s)
        if o not in var_dict:
            var_dict[o] = Variable(o)
        query.append((var_dict[s], ex[p], var_dict[o]))
        tamplate.append((s, p, o))
        # print(s, p, o)
    iterator = hdt.search_join(query)
    for row in iterator:
        if len(row) != 3:
            continue
        if row.A == row.B or row.B == row.C or row.A == row.C:
            continue
        # print(row)
        graph.add_edge(row.A.replace("http://example.org/",""), row.B.replace("http://example.org/",""))
        # for tamp in tamplate:
            # print(tamp)
            # print(row[tamp[0]], ex[tamp[1]], row[tamp[2]])
            # with open("forget_data/general_rules.nt", "a+") as file:
                # file.write(f"<{row[tamp[0]]}> <{ex[tamp[1]]}> <{row[tamp[2]]}> .\n")
        # break
    # g.serialize("forget_data/general_rules.nt", format="nt")
    # break
print(graph)
# g_test = Graph()
# g_test.parse("forget_data/general_rules.nt", format="nt")