import pandas as pd

file1 = pd.read_csv('exp_data/KnowlegeGraph.tsv', delimiter='\t', header = None)

triples = set()

for index, row in file1.iterrows():
    s = str(row[0])+str(row[1])
    p = str(row[2])
    o = str(row[3])+str(row[4])
    triples.add(f"{p}({s},{o})")
with open("exp_data/KnowlegeGraph.txt", "a+") as f:
    for triple in triples:
        f.write(triple+"\n")