import networkx as nx
import pandas as pd

G = nx.Graph()
kg_file = pd.read_csv('exp_data/KnowlegeGraph.tsv', sep='\t', header=None)
for it, row in kg_file.iterrows():
    s = str(row[0])+str(row[1])
    p = str(row[2])
    o = str(row[3])+str(row[4])
    G.add_edge(s, o)
# sample_path = "user1112	movie518	user629	movie466	user1112	movie518"
# impact_score = measure_impact_wsc(G, sample_path, "user629","movie518")