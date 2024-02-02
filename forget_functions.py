from rdflib import Graph, Namespace
from rdflib_hdt import HDTStore, optimize_sparql, HDTDocument
import numpy as np
import networkx as nx
import random

def check_exist_triple(document: HDTDocument, s, p ,o):
    ex = Namespace("http://example.org/")
    _, cardinality = document.search((ex[s], ex[p], ex[o]))
    if cardinality > 0:
        return True
    else:
        return False
    
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

def measure_impact_wsc(G:nx.Graph(), path:str, forget_source:str, forget_target:str, alpha=0.15, theta=0.1):
    """Measure the impact of a path on the PPR estimates of a target node
    G: Graph (DiGraph or Graph in nx)
    path: Path
    forget_source: Source node
    forget_target: Target node
    alpha: Teleport probability
    theta: Error parameter
    
    Returns: Impact score
    """
    lambda_function=lambda u: G.degree(u)
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

def RBS_optimized(G, target, alpha, theta, lambda_function):
    V = list(G.nodes())
    node_index = {node: idx for idx, node in enumerate(V)}  # Cache node indices
    L = int(np.log(1/theta) / np.log(1/alpha))
    estimates = np.zeros((L+1, len(V)))
    target_idx = node_index[target]
    estimates[0, target_idx] = alpha

    degrees = {node: G.degree(node) for node in V}  # Pre-calculate degrees

    for l in range(L):
        for node in V:
            node_idx = node_index[node]
            if estimates[l, node_idx] > 0:
                for u in G.neighbors(node):
                    dout_u = degrees[u]
                    est = estimates[l, node_idx]
                    if dout_u <= lambda_function(u) * (1-alpha) * est / alpha / theta:
                        estimates[l+1, node_index[u]] += (1-alpha) * est / dout_u
                    else:
                        r = random.random()
                        if r < alpha * theta / lambda_function(u):
                            estimates[l+1, node_index[u]] += alpha * theta / lambda_function(u)

    final_estimates = np.sum(estimates, axis=0)
    return {V[idx]: val for idx, val in enumerate(final_estimates)}

def zero_RBS_for_all_targets(G, targets, alpha=0.15, theta=0.1, lambda_function=None):
    lambda_function = lambda u: G.degree(u)
    output_set = set()
    for target in targets:
        optimized_dict = RBS_optimized(G, target, alpha, theta, lambda_function)
        for source in get_all_0_value_keys(optimized_dict):
            if G.has_edge(source, target):
                output_set.add((source, target))
    return output_set

def get_all_0_value_keys(dictionary):
    return [key for key in dictionary if dictionary[key] == 0]

def find_least_model(init_G,update_G, rule):
    """
    Args:
        init_G: initial graph
        rule: rule in string
        
    Returns:
        updated or non-updated graph
        boolean value indicating whether the graph is updated
        """
    assert isinstance(init_G, Graph)
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

def get_least_model(rule_list:list):
    init_least_model = set()
    for rule in rule_list:
        head = rule.split(" <= ")[0]
        init_least_model.add(head)
        body = rule.split(" <= ")[1]
        body_atoms = body.split(" & ")
        init_least_model.update(body_atoms)
    return init_least_model

def check_least_model(rule_list:list, least_model:set):
    for rule in rule_list:
        head = rule.split(" <= ")[0]
        body = rule.split(" <= ")[1]
        body_atoms = body.split(" & ")
        if head not in least_model or not least_model.issuperset(set(body_atoms)):
            return False
    return True

def get_low_impact_WSC(G:nx.Graph(), path_list:list, targets, alpha=0.15, theta=0.1, impact_threshold = 0.0):
    low_impact_atoms = set()
    if impact_threshold >= 0:
        low_impact_atoms.update(zero_RBS_for_all_targets(G, targets, alpha, theta))