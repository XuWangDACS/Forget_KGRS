import rdflib
import pandas as pd

g = rdflib.Graph()
g.parse("exp_data/KnowlegeGraph.ttl", format="turtle")

# Construct query based on rule: recommend(A, B) <= watched(A, C) & cinematography(C, D) & cinematography(B, D)
query1 = """
prefix ex: <http://example.org/>
construct {
    ?A ex:recommend ?B .
}
where {
    ?A ex:watched ?C .
    ?C ex:cinematography ?D .
    ?B ex:cinematography ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & produced_by_company(C, D) & produced_by_company(B, D)
query2 = """
prefix ex: <http://example.org/>
construct {
    ?A ex:recommend ?B .
}
where {
    ?A ex:watched ?C .
    ?C ex:produced_by_company ?D .
    ?B ex:produced_by_company ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & belong_to(C, D) & belong_to(B, D)
query3 = """
prefix ex: <http://example.org/>
construct {
    ?A ex:recommend ?B .
}
where {
    ?A ex:watched ?C .
    ?C ex:belong_to ?D .
    ?B ex:belong_to ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & starring(C, D) & starring(B, D)
query4 = """
prefix ex: <http://example.org/>
construct {
    ?A ex:recommend ?B .
}
where {
    ?A ex:watched ?C .
    ?C ex:starring ?D .
    ?B ex:starring ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & edited_by(C, D) & edited_by(B, D)
query5 = """
prefix ex: <http://example.org/>
construct {
    ?A ex:recommend ?B .
}
where {
    ?A ex:watched ?C .
    ?C ex:edited_by ?D .
    ?B ex:edited_by ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & produced_by_producer(C, D) & produced_by_producer(B, D)
query6 = """
prefix ex: <http://example.org/>
construct {
    ?A ex:recommend ?B .
}
where {
    ?A ex:watched ?C .
    ?C ex:produced_by_producer ?D .
    ?B ex:produced_by_producer ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & wrote_by(C, D) & wrote_by(B, D)
query7 = """
prefix ex: <http://example.org/>
construct {
    ?A ex:recommend ?B .
}
where {
    ?A ex:watched ?C .
    ?C ex:wrote_by ?D .
    ?B ex:wrote_by ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & directed_by(C, D) & directed_by(B, D)
query8 = """
prefix ex: <http://example.org/>
construct {
    ?A ex:recommend ?B .
}
where {
    ?A ex:watched ?C .
    ?C ex:directed_by ?D .
    ?B ex:directed_by ?D .
}
"""

# rule: recommend(A, B) <= watched(A, C) & watched(D, C) & watched(D, B)
query9 = """
prefix ex: <http://example.org/>
construct {
    ?A ex:recommend ?B .
}
where {
    ?A ex:watched ?C .
    ?D ex:watched ?C .
    ?D ex:watched ?B .
}
"""

# Print results
for result in g.query(query1):
    print(result[0], " -> ",result[1])
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

g.close()