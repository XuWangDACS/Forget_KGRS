from pyDatalog import pyDatalog
import pandas as pd

pyDatalog.create_terms('A,B,C,D,X,Y')
pyDatalog.create_terms('recommend')
relations_set = {'starring', 'produced_by_producer', 'directed_by', 'edited_by', 'cinematography', 'wrote_by', 'belong_to', 'watched', 'produced_by_company'}
for relation in relations_set:
    pyDatalog.create_terms(relation)

file = pd.read_csv('exp_data/KnowlegeGraph.tsv', delimiter='\t', header = None)
for index, row in file.iterrows():
    s = str(row[0])+str(row[1])
    p = str(row[2])
    o = str(row[3])+str(row[4])
    exec(f"+{p}('{s}', '{o}')")

recommend(A, B) <= watched(A, C) & cinematography(C, D) & cinematography(B, D)
recommend(A, B) <= watched(A, C) & produced_by_company(C, D) & produced_by_company(B, D)
recommend(A, B) <= watched(A, C) & belong_to(C, D) & belong_to(B, D)
recommend(A, B) <= watched(A, C) & starring(C, D) & starring(B, D)
recommend(A, B) <= watched(A, C) & edited_by(C, D) & edited_by(B, D)
recommend(A, B) <= watched(A, C) & produced_by_producer(C, D) & produced_by_producer(B, D)
recommend(A, B) <= watched(A, C) & wrote_by(C, D) & wrote_by(B, D)
recommend(A, B) <= watched(A, C) & directed_by(C, D) & directed_by(B, D)
recommend(A, B) <= watched(A, C) & watched(D, C) & watched(D, B)

results = recommend(X, Y)

for result in results:
    print(result[0], " -> ",result[1])