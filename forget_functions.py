from rdflib import Graph, Namespace
from rdflib_hdt import HDTStore, optimize_sparql, HDTDocument
import pandas as pd
import numpy as np
import networkx as nx
import random
import os
from extract_rules_from_paths import extract_from_line


def parse_rules(rule_path:str):
    assert os.path.isfile(rule_path), f"{rule_path} is not a valid file path"
    file = pd.read_csv(rule_path, header=None,  delimiter=',')
    rule_list = []
    for _, row in file.iterrows():
        path = row['path']
        body,body_tsv, tpath = extract_from_line(path)
        rule = f"recommend(user{row['uid']},movie{row['pid']}) <= {' & '.join(body)}"
        rule_list.append(rule)
    return rule_list

def build_pforget_search_space(forget_rules:list):
    search_space = set()
    for rule in forget_rules:
        head = rule.split(" <= ")[0]
        body = rule.split(" <= ")[1]
        body_atoms = body.split(" & ")
        for atom in body_atoms:
            s, p, o = get_s_p_o(atom)
            search_space.add((s,p,o))
    return search_space

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

def RBS_optimized(G, target, alpha=0.15, theta=0.1):
    lambda_function = lambda u: G.degree(u)
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
        
def get_predicate_degree_centrality(hdt:HDTDocument, forget_triples:list = []):
    DiG = nx.DiGraph()
    predicate_set = set()
    triples, _ = hdt.search((None, None, None))
    for s, p, o in triples:
        sub = str(s).replace("http://example.org/","")
        pre = str(p).replace("http://example.org/","")
        obj = str(o).replace("http://example.org/","")
        if (sub,pre,obj) in forget_triples:
            continue
        predicate_set.add(pre)
        DiG.add_edge(sub,pre)
        DiG.add_edge(pre,obj)
    degree_centrality = nx.degree_centrality(DiG)
    predicate_degree_centrality = {node: centrality for node, centrality in degree_centrality.items() if node in predicate_set}
    return predicate_degree_centrality

def get_entity_page_rank(hdt:HDTDocument, forget_triples:list = []):
    DiG = nx.DiGraph()
    triples, _ = hdt.search((None, None, None))
    for s, p, o in triples:
        sub = str(s).replace("http://example.org/","")
        pre = str(p).replace("http://example.org/","")
        obj = str(o).replace("http://example.org/","")
        if (sub,pre,obj) in forget_triples:
            continue
        DiG.add_edge(sub,obj)
    return nx.pagerank(DiG)
        
def get_WSC_cheap_scores_triples(hdt:HDTDocument, forget_triples:list = [], alpha=0.5, beta = 0.5):
    predicate_degree_centrality = get_predicate_degree_centrality(hdt,forget_triples)
    node_pagerank = get_entity_page_rank(hdt,forget_triples)
    WSC_score_dict = {}
    triples, cardinality = hdt.search((None, None, None))
    for s, p, o in triples:
        sub = str(s).replace("http://example.org/","")
        pre = str(p).replace("http://example.org/","")
        obj = str(o).replace("http://example.org/","")
        WSC_score = alpha * predicate_degree_centrality[pre] + beta * (node_pagerank[sub] + node_pagerank[obj])
        WSC_score_dict[(sub,pre,obj)] = WSC_score
    return WSC_score_dict

def get_RBS_dict(hdt:HDTDocument, target:str, forget_triples:list = [], alpha=0.15, theta=0.1):
    G = nx.Graph()
    triples, _ = hdt.search((None, None, None))
    for s, p, o in triples:
        sub = str(s).replace("http://example.org/","")
        pre = str(p).replace("http://example.org/","")
        obj = str(o).replace("http://example.org/","")
        if (sub,pre,obj) in forget_triples:
            continue
        G.add_edge(sub,obj)
    return RBS_optimized(G, target, alpha, theta)
    

def get_WSC_cheap_scores_rules(hdt:HDTDocument,rule_list:list,forget_triples:list, alpha=0.5, beta = 0.5, rule_alpha=0.5, rule_beta=0.5):
    WSC_triple_dict = get_WSC_cheap_scores_triples(hdt, forget_triples, alpha, beta)
    WSC_score_dict = {}
    for rule in rule_list:
        head = rule.split(" <= ")[0]
        source, _, target = get_s_p_o(head)
        RBS_dict = get_RBS_dict(hdt, target, forget_triples)
        body = rule.split(" <= ")[1]
        body_atoms = body.split(" & ")
        body_score = 0.0
        for atom in body_atoms:
            predicate, subject, object = get_s_p_o(atom)
            triple_score = WSC_triple_dict[(subject,predicate,object)]
            body_score += triple_score * rule_alpha + (RBS_dict[subject] + RBS_dict[object]) * 0.5 * rule_beta
        WSC_score_dict[rule] = body_score
    return WSC_score_dict

def pforget_LM(rule_list:list, search_space:set):
    forget_triples = set()
    least_model = get_least_model(rule_list)
    for triple in search_space:
        if triple not in least_model:
            forget_triples.add(triple)
    return forget_triples

def pforget_WSC(hdt:HDTDocument, rule_list:list, search_space:set, alpha=0.5, beta = 0.5, rule_alpha=0.5, rule_beta=0.5, ratio=0.95):
    forget_triples = set()
    original_WSC_dict = get_WSC_cheap_scores_rules(hdt, rule_list, [], alpha, beta, rule_alpha, rule_beta)
    sorted_dict = sorted(WSC_score_dict.items(), key=lambda x: x[1], reverse=True)
    for rule, _ in sorted_dict:
        head = rule.split(" <= ")[0]
        source, _, target = get_s_p_o(head)
        if (source,_,target) in search_space:
            forget_triples.add((source,_,target))
    return forget_triples