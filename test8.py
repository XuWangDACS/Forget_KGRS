import rdflib
from construct_query import *

g = rdflib.Graph()

g_new = rdflib.Graph()

g.parse("forget_data/KnowlegeGraph.ttl", format="ttl")

construct1 = g.query(query1)
for triple in construct1:
    g_new.add(triple)
    
construct2 = g.query(query2)
for triple in construct2:
    g_new.add(triple)
    
construct3 = g.query(query3)
for triple in construct3:
    g_new.add(triple)
    
construct4 = g.query(query4)
for triple in construct4:
    g_new.add(triple)
    
construct5 = g.query(query5)
for triple in construct5:
    g_new.add(triple)
    
construct6 = g.query(query6)
for triple in construct6:
    g_new.add(triple)
    
construct7 = g.query(query7)
for triple in construct7:
    g_new.add(triple)
    
construct8 = g.query(query8)
for triple in construct8:
    g_new.add(triple)
    
construct9 = g.query(query9)
for triple in construct9:
    g_new.add(triple)
    
g_new.serialize(destination='forget_data/construct.ttl', format='ttl')