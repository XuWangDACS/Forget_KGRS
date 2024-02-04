# Construct query based on rule: recommend(A, B) <= watched(A, C) & cinematography(C, D) & cinematography(B, D)
query1 = """
prefix ex: <http://example.org/>
CONSTRUCT {
    ?A ex:watched ?C .
    ?C ex:cinematography ?D .
    ?B ex:cinematography ?D .
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
CONSTUCT {
    ?A ex:watched ?C .
    ?C ex:produced_by_company ?D .
    ?B ex:produced_by_company ?D .
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
CONSTRUCT {
    ?A ex:watched ?C .
    ?C ex:belong_to ?D .
    ?B ex:belong_to ?D .
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
CONSTRUCT {
    ?A ex:watched ?C .
    ?C ex:starring ?D .
    ?B ex:starring ?D .
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
CONSTRUCT {
    ?A ex:watched ?C .
    ?C ex:edited_by ?D .
    ?B ex:edited_by ?D .
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
CONSTRUCT {
    ?A ex:watched ?C .
    ?C ex:produced_by_producer ?D .
    ?B ex:produced_by_producer ?D .
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
CONSTRUCT {
    ?A ex:watched ?C .
    ?C ex:wrote_by ?D .
    ?B ex:wrote_by ?D .
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
CONSTRUCT {
    ?A ex:watched ?C .
    ?C ex:directed_by ?D .
    ?B ex:directed_by ?D .
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
CONSTRUCT {
    ?A ex:watched ?C .
    ?D ex:watched ?C .
    ?D ex:watched ?B .
}
where {
    ?A ex:watched ?C .
    ?D ex:watched ?C .
    ?D ex:watched ?B .
}
"""