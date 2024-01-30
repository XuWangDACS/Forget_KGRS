import networkx as nx
import pandas as pd
from Function import RBS, RBS_optimized
import time

G = nx.Graph()

kg_file = pd.read_csv('exp_data/KnowlegeGraph.tsv', sep='\t', header=None)

for it, row in kg_file.iterrows():
    s = str(row[0])+str(row[1])
    p = str(row[2])
    o = str(row[3])+str(row[4])
    G.add_edge(s, o)        
    
sample_path = "user1112	movie518	user629	movie466	user1112	movie518"

source = "user1112"
target = "movie518"  # Target node
alpha = 0.15  # Teleport probability
theta = 0.1  # Error parameter
lambda_function = lambda u: G.degree(u)  # Lambda function based on node degree
start_time = time.time()
ppr_estimates = RBS_optimized(G, target, alpha, theta, lambda_function)
end_time = time.time()
execution_time = abs(start_time - end_time)
print("Execution time:",execution_time)
# print(ppr_estimates)

optimized_dict = {key: value for key, value in ppr_estimates.items() if value != 0}

# print(optimized_dict)

all_paths = nx.all_simple_paths(G,source, target, cutoff=3)

path_score_dict = {}

for path in all_paths:
    path_score = 0
    for node in path:
        if node in optimized_dict:
            path_score += optimized_dict[node]
    path_score_dict[str(path)] = path_score

# print(path_score_dict)

# sort dict based on value
sorted_dict = sorted(path_score_dict.items(), key=lambda x: x[1], reverse=True)
max_path_score = sorted_dict[0][1]

# sort dict based on value, cedescending
sorted_dict = sorted(path_score_dict.items(), key=lambda x: x[1], reverse=False)
min_path_score = sorted_dict[0][1]

sample_nodes = sample_path.split("\t")[2:]
print(sample_nodes)

sample_score = 0

for node in sample_nodes:
    if node in optimized_dict:
        sample_score += optimized_dict[node]

print(sample_score)

normalized_score = abs(sample_score - min_path_score) / abs(max_path_score - min_path_score)

print(normalized_score)

# print top 5 paths with highest score
# print(sorted_dict[:5])
