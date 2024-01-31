import rdflib
import pandas as pd
from Forget_hdt import get_s_p_o

# g = rdflib.Graph()
# g.parse("exp_data/KnowlegeGraph.ttl", format="turtle")

# Construct query based on rule: recommend(A, B) <= watched(A, C) & cinematography(C, D) & cinematography(B, D)
query1 = """
prefix ex: <http://example.org/>
SELECT ?A ?B
where {
    ?A ex:watched ?C .
    ?C ex:cinematography ?D .
    ?B ex:cinematography ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & produced_by_company(C, D) & produced_by_company(B, D)
query2 = """
prefix ex: <http://example.org/>
SELECT ?A ?B
where {
    ?A ex:watched ?C .
    ?C ex:produced_by_company ?D .
    ?B ex:produced_by_company ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & belong_to(C, D) & belong_to(B, D)
query3 = """
prefix ex: <http://example.org/>
SELECT ?A ?B
where {
    ?A ex:watched ?C .
    ?C ex:belong_to ?D .
    ?B ex:belong_to ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & starring(C, D) & starring(B, D)
query4 = """
prefix ex: <http://example.org/>
SELECT ?A ?B
where {
    ?A ex:watched ?C .
    ?C ex:starring ?D .
    ?B ex:starring ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & edited_by(C, D) & edited_by(B, D)
query5 = """
prefix ex: <http://example.org/>
SELECT ?A ?B
where {
    ?A ex:watched ?C .
    ?C ex:edited_by ?D .
    ?B ex:edited_by ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & produced_by_producer(C, D) & produced_by_producer(B, D)
query6 = """
prefix ex: <http://example.org/>
SELECT ?A ?B
where {
    ?A ex:watched ?C .
    ?C ex:produced_by_producer ?D .
    ?B ex:produced_by_producer ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & wrote_by(C, D) & wrote_by(B, D)
query7 = """
prefix ex: <http://example.org/>
SELECT ?A ?B
where {
    ?A ex:watched ?C .
    ?C ex:wrote_by ?D .
    ?B ex:wrote_by ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & directed_by(C, D) & directed_by(B, D)
query8 = """
prefix ex: <http://example.org/>
SELECT ?A ?B
where {
    ?A ex:watched ?C .
    ?C ex:directed_by ?D .
    ?B ex:directed_by ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & watched(D, C) & watched(D, B)
query9 = """
prefix ex: <http://example.org/>
SELECT ?A ?B
where {
    ?A ex:watched ?C .
    ?D ex:watched ?C .
    ?D ex:watched ?B .
}
"""

# Print results
# for result in g.query(query1):
#     print(result)
# for result in g.query(query2):
#     print(result[0], " -> ",result[1])
# for result in g.query(query3):
#     print(result[0], " -> ",result[1])
# for result in g.query(query4):
#     print(result[0], " -> ",result[1])
# for result in g.query(query5):
#     print(result[0], " -> ",result[1])
# for result in g.query(query6):
#     print(result[0], " -> ",result[1])
# for result in g.query(query7):
#     print(result[0], " -> ",result[1])
# for result in g.query(query8):
#     print(result[0], " -> ",result[1])
# for result in g.query(query9):
#     print(result[0], " -> ",result[1])

# g.close()

def find_least_model(init_G,update_G, rule):
    """
    Args:
        init_G: initial graph
        rule: rule in string
        
    Returns:
        updated or non-updated graph
        boolean value indicating whether the graph is updated
        """
    assert isinstance(init_G, rdflib.Graph)
    update = False
    ex = "http://example.org/"
    head = rule.split(" <= ")[0]
    s, p, o = get_s_p_o(head)
    head_query = f"<{ex}{s}> <{ex}{p}> <{ex}{o}> ."
    body = rule.split(" <= ")[1]
    body_atoms = body.split(" & ")
    body_query = ""
    for atom in body_atoms:
        subject, predicate, object = get_s_p_o(atom)
        body_query += f"<{ex}{subject}> <{ex}{predicate}> <{ex}{object}> .\n"
    query = f"""
    prefix ex: <http://example.org/>
    Insert {{
        {head_query}
    }}
    where {{
        {body_query}
    }}
    """
    
    init_len = 0
    update_len = -1
    while(init_len != update_len):
        init_len = len(init_G)
        init_G.update(query)
        update_len = len(init_G)
        update = True
    return update, update_G

rule = "recommend(user3,movie31) <= watched(user3,movie986) & watched(user238,movie986) & watched(user238,movie31)"

rule_list = []
with open("exp_data/rules_exp1.txt", "r") as f:
    for line in f:
        rule_list.append(line.strip())

head = rule.split(" <= ")[0]
body = rule.split(" <= ")[1]
body_atoms = body.split(" & ")
initial_G = rdflib.Graph()
# initial_G.add((rdflib.URIRef("http://example.org/user3"), rdflib.URIRef("http://example.org/watched"), rdflib.URIRef("http://example.org/movie986")))
# initial_G.add((rdflib.URIRef("http://example.org/user238"), rdflib.URIRef("http://example.org/watched"), rdflib.URIRef("http://example.org/movie986")))
# initial_G.add((rdflib.URIRef("http://example.org/user238"), rdflib.URIRef("http://example.org/watched"), rdflib.URIRef("http://example.org/movie31")))
initial_G.parse("exp_data/KnowlegeGraph.ttl", format="turtle")
update_G = rdflib.Graph()

# from tqdm import tqdm

# update = False
# for rule in tqdm(rule_list):
#     update = find_least_model(initial_G, rule)
# if update:
#     print(initial_G.serialize(format="nt"))

update,update_G = find_least_model(initial_G,update_G, rule)
# print(initial_G.serialize(format="nt"))