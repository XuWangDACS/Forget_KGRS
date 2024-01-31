from rdflib import Graph, Namespace
from rdflib_hdt import HDTStore, optimize_sparql, HDTDocument

# optimize_sparql()

def check_exist_triple(document: HDTDocument, s, p ,o):
    ex = Namespace("http://example.org/")
    _, cardinality = document.search((ex[s], ex[p], ex[o]))
    if cardinality > 0:
        return True
    else:
        return False

# graph = Graph(store=HDTStore("exp_data/KnowlegeGraph.hdt"))

ex = Namespace("http://example.org/")
    
# General rule recommend(A, B) :- watched(A, C), cinematography(C, D), cinematography(B, D).
# C = "user629"
# D = "movie466"
# qres = graph.query("""
# PREFIX ex: <http://example.org/>
# SELECT ?A ?B WHERE {
#     ?A ex:watched ex:"""+C+""" .
#     ex:"""+C+""" ex:cinematography ex:"""+D+""" .
#     ?B ex:cinematography ex:"""+D+""" .
#     values ?A {ex:user1112}
#     values ?B {ex:movie518}
# }""")
# for row in qres:
#     print(f"{row.A} {row.B}")


document = HDTDocument("exp_data/KnowlegeGraph.hdt")

rule = "recommend(user3,movie31) <= watched(user3,movie986) & watched(user238,movie986) & watched(user238,movie31)"
head = rule.split(" <= ")[0]
body = rule.split(" <= ")[1]
body_atoms = body.split(" & ")

def get_s_p_o(atom):
    """
    Args:
        atom: predicate(subject,object)

    Returns:
        subject, predicate, object
    """
    predicate = atom.split("(")[0]
    subject = atom.split("(")[1].split(",")[0]
    object = atom.split("(")[1].split(",")[1][:-1]
    return subject, predicate, object

def check_ground_rule_satisfy(document: HDTDocument, rule):
    head = rule.split(" <= ")[0]
    body = rule.split(" <= ")[1]
    body_atoms = body.split(" & ")
    for atom in body_atoms:
        predicate, subject, object = get_s_p_o(atom)
        if not check_exist_triple(document, subject, predicate, object):
            # print("Not satisfied triple in body:", subject, predicate, object)
            return False
    return True

# print(check_ground_rule_satisfy(document, rule))

# print(len(iterator))

# for row in iterator:
#   print(row)
