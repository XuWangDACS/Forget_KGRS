import networkx as nx
# import pandas as pd
from Function import RBS, RBS_optimized

# G = nx.Graph()

# kg_file = pd.read_csv('exp_data/KnowlegeGraph.tsv', sep='\t', header=None)

# for it, row in kg_file.iterrows():
#     s = str(row[0])+str(row[1])
#     p = str(row[2])
#     o = str(row[3])+str(row[4])
#     G.add_edge(s, o)

def measure_impact_wsc(G:nx.Graph(), path:str, forget_source:str, forget_target:str, alpha=0.15, theta=0.1, lambda_function=lambda u: G.degree(u)):
    """Measure the impact of a path on the PPR estimates of a target node
    G: Graph (DiGraph or Graph in nx)
    path: Path
    forget_source: Source node
    forget_target: Target node
    alpha: Teleport probability
    theta: Error parameter
    lambda_function: Lambda function based on node degree
    
    Returns: Impact score
    """
    
    if not G.has_edge(forget_source, forget_target):
        return 0
    
    split_path = path.split("\t")
    source = split_path[0]
    target = split_path[1]
    all_paths = nx.all_simple_paths(G, source, target, cutoff=3)
    optimized_dict = RBS_optimized(G, target, alpha, theta, lambda_function)
    G.remove_edge(forget_source, forget_target)
    optimized_dict_forget = RBS_optimized(G, target, alpha, theta, lambda_function)
    G.add_edge(forget_source, forget_target)
    
    path_score_dict = {}
    path_score_dict_forget = {}

    for path in all_paths:
        path_score = 0
        path_score_forget = 0
        for node in path:
            if node in optimized_dict:
                path_score += optimized_dict[node]
            if node in optimized_dict_forget:
                path_score_forget += optimized_dict_forget[node]
        path_score_dict[str(path)] = path_score
        path_score_dict_forget[str(path)] = path_score_forget
    
    sorted_dict = sorted(path_score_dict.items(), key=lambda x: x[1], reverse=True)
    max_path_score = sorted_dict[0][1]
    min_path_score = sorted_dict[-1][1]
    
    sorted_dict_forget = sorted(path_score_dict_forget.items(), key=lambda x: x[1], reverse=True)
    max_path_score_forget = sorted_dict_forget[0][1]
    min_path_score_forget = sorted_dict_forget[-1][1]
    
    given_path_nodes = path.split("\t")[2:]
    given_path_score = 0
    given_path_score_forget = 0
    
    for node in given_path_nodes:
        if node in optimized_dict:
            given_path_score += optimized_dict[node]
        if node in optimized_dict_forget:
            given_path_score_forget += optimized_dict_forget[node]
    
    normalized_score = abs(given_path_score - min_path_score) / abs(max_path_score - min_path_score)
    normalized_score_forget = abs(given_path_score_forget - min_path_score_forget) / abs(max_path_score_forget - min_path_score_forget)
    impact_score = normalized_score_forget - normalized_score
    return impact_score

# sample_path = "user1112	movie518	user629	movie466	user1112	movie518"
# impact_score = measure_impact_wsc(G, sample_path, "user629","movie518")
# print(impact_score)