from rdflib import Graph, Namespace
from rdflib_hdt import HDTStore, optimize_sparql, HDTDocument
import pandas as pd
import numpy as np
import networkx as nx
import random
import os
from tqdm import tqdm
from extract_rules_from_paths import extract_from_line
import pickle
from scipy.sparse import lil_matrix
import pickle
# import graph_tool.all as gt_all

predicate_set = {'starring', 'produced_by_producer', 'directed_by', 'edited_by', 'cinematography', 'wrote_by', 'belong_to', 'produced_by_company', 'watched'}

def construct_graph_dict_from_hdt(hdt:HDTDocument):
    graph_dict = {}
    ex = Namespace("http://example.org/")
    for relation in tqdm(predicate_set,desc="Creating Graphs"):
        graph_dict[relation] = nx.DiGraph()
        triples,_  = hdt.search((None, ex[relation], None))
        for s,p,o in triples:
            graph_dict[relation].add_edge(s.replace("http://example.org/",""), o.replace("http://example.org/",""))

def parse_rules(rule_path:str):
    file = pd.read_csv(rule_path, delimiter=',',header = 0)
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

def build_iforget_search_space(hdt:HDTDocument):
    search_space = set()
    triples, _ = hdt.search((None, None, None))
    for s, p, o in triples:
        sub = str(s).replace("http://example.org/","")
        pre = str(p).replace("http://example.org/","")
        obj = str(o).replace("http://example.org/","")
        search_space.add((sub,pre,obj))
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
        subject, predicate, object = get_s_p_o(atom)
        if not check_exist_triple(document, subject, predicate, object):
            # print("Not satisfied triple in body:", subject, predicate, object)
            return False
    return True

def RBS_optimized(G, target, alpha=0.2, theta=0.1):
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

def RBS_optimized_3hops(G, target, alpha=0.2, theta=0.1):
    lambda_function = lambda u: G.degree(u)
    V = list(G.nodes())
    node_index = {node: idx for idx, node in enumerate(V)}  # Cache node indices
    L = 3  # Set the number of iterations to 3 for max hop=3
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

def get_predicate_degree_centrality(DiG:nx.DiGraph()):
    # DiG = nx.DiGraph()
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
            subject, predicate, object = get_s_p_o(atom)
            triple_score = WSC_triple_dict[(subject,predicate,object)]
            body_score += triple_score * rule_alpha + (RBS_dict[subject] + RBS_dict[object]) * 0.5 * rule_beta
        WSC_score_dict[rule] = body_score
    return WSC_score_dict

def forget_LM(rule_list:list, search_space:set):
    forget_triples = set()
    least_model = get_least_model(rule_list)
    for triple in tqdm(search_space, desc="analysing search space with least model impact"):
        if triple not in least_model:
            forget_triples.add(triple)
    return forget_triples

def get_all_triples_from_rule_list(rule_list:list):
    triples = set()
    for rule in rule_list:
        head = rule.split(" <= ")[0]
        body = rule.split(" <= ")[1]
        body_atoms = body.split(" & ")
        for atom in body_atoms:
            s, p, o = get_s_p_o(atom)
            triples.add((s,p,o))
    return triples

def weighted_average_score(path, node_scores, edge_scores, w_n=0.3, w_e=0.7):
    node_score = sum(node_scores[node] for node in path)
    edge_score = sum(edge_scores[(path[i], path[i+1])] for i in range(len(path)-1))
    total_score = w_n * node_score + w_e * edge_score
    return total_score / (w_n * len(path) + w_e * (len(path)-1))

def weighted_average_score_triple(triple_list:list, node_scores, edge_scores, w_n=0.3, w_e=0.7):
    node_score = 0.0
    edge_score = 0.0
    for triple in triple_list:
        s, p ,o = get_s_p_o(triple)

    node_score = sum(node_scores[node] for node in triple_list)
    edge_score = sum(edge_scores[(triple_list[i], triple_list[i+1])] for i in range(len(triple_list)-1))
    total_score = w_n * node_score + w_e * edge_score
    return total_score / (w_n * len(triple_list) + w_e * (len(triple_list)-1))

def ppr_score(G:nx.Graph(), target):
    personalization = {node: 1 if node == target else 0 for node in G.nodes()}
    return nx.pagerank(G, personalization=personalization)

def check_with_WSC(G:nx.Graph(),DiG:nx.DiGraph(), rule_list:list, forget_triple, RBS_dicts:dict, predicate_dict:dict, alpha=0.3, beta = 0.7):
    w_n = alpha
    w_e = beta
    s, p ,o = get_s_p_o(forget_triple)
    G.remove_edge(s,o)
    RBS_new = RBS_optimized(G, o)
    G.add_edge(s,o)
    DiG.remove_edge(s,p)
    DiG.remove_edge(p,o)
    predicate_dict_new = get_predicate_degree_centrality(DiG)
    DiG.add_edge(s,p)
    DiG.add_edge(p,o)
    triple_score = 0.0
    for rule in rule_list:
        head = rule.split(" <= ")[0]
        source, _, target = get_s_p_o(head)
        RBS_old_target = RBS_dicts[target]
        RBS_new_target = RBS_new[target]
        body = rule.split(" <= ")[1]
        body_atoms = body.split(" & ")
        body_score_old = 0.0
        body_score_new = 0.0
        for atom in body_atoms:
            subject, predicate, object = get_s_p_o(atom)
            body_score_old += w_e * predicate_dict[predicate] + w_n * (predicate_dict[subject] + predicate_dict[object])
            body_score_new += w_e * predicate_dict_new[predicate] + w_n * (predicate_dict_new[subject] + predicate_dict_new[object])
        triple_score += (body_score_new - body_score_old) / (3.0*w_n + 2.0*w_e)
    return triple_score

def check_with_WSC_PPR(G:nx.Graph(),DiG:nx.DiGraph(), rule_list:list, forget_triple,PPR_dicts:dict, predicate_dict:dict, alpha=0.3, beta = 0.7):
    w_n = alpha
    w_e = beta
    s, p ,o = forget_triple
    G.remove_edge(s,o)
    DiG.remove_edge(s,p)
    DiG.remove_edge(p,o)
    predicate_dict_new = get_predicate_degree_centrality(DiG)
    DiG.add_edge(s,p)
    DiG.add_edge(p,o)
    triple_score = 0.0
    for rule in rule_list:
        head = rule.split(" <= ")[0]
        source, _, target = get_s_p_o(head)
        ppr_new = ppr_score(G, target)
        body = rule.split(" <= ")[1]
        body_atoms = body.split(" & ")
        body_score_old = 0.0
        body_score_new = 0.0
        for atom in body_atoms:
            subject, predicate, object = get_s_p_o(atom)
            body_score_old += w_e * predicate_dict[predicate] + w_n * (PPR_dicts[target][subject] + PPR_dicts[target][object])
            body_score_new += w_e * predicate_dict_new[predicate] + w_n * (ppr_new[subject] + ppr_new[object])
        triple_score += (body_score_new - body_score_old) / (3.0*w_n + 2.0*w_e)
    G.add_edge(s,o)
    return triple_score

def check_with_WSC_PRR_simple(G:nx.Graph(),DiG:nx.DiGraph(), rule_list:list, forget_triple,PPR_dicts:dict, predicate_dict:dict, alpha=0.3, beta = 0.7):
    w_n = alpha
    w_e = beta
    s, p ,o = forget_triple
    
    DiG.remove_edge(s,p)
    DiG.remove_edge(p,o)
    predicate_dict_new = get_predicate_degree_centrality(DiG)
    DiG.add_edge(s,p)
    DiG.add_edge(p,o)
    triple_score = 0.0
    for rule in rule_list:
        head = rule.split(" <= ")[0]
        source, _, target = get_s_p_o(head)
        # ppr_new = ppr_score(G, target)
        body = rule.split(" <= ")[1]
        body_atoms = body.split(" & ")
        body_score_old = 0.0
        body_score_new = 0.0
        for atom in body_atoms:
            subject, predicate, object = get_s_p_o(atom)
            node_score = PPR_dicts[target][subject] + PPR_dicts[target][object]
            if (PPR_dicts[target][subject] + PPR_dicts[target][object]) == 0.0:
                continue
            body_score_old += w_e * predicate_dict[predicate] + w_n * (PPR_dicts[target][subject] + PPR_dicts[target][object])
            body_score_new += w_e * predicate_dict_new[predicate] + w_n * (PPR_dicts[target][subject] + PPR_dicts[target][object])
        triple_score += (body_score_new - body_score_old) / (3.0*w_n + 2.0*w_e)
    return triple_score

def get_all_targets_from_rule_list(rule_list:list):
    target_list = set()
    for rule in rule_list:
        head = rule.split(" <= ")[0]
        source, _, target = get_s_p_o(head)
        target_list.add(target)
    return target_list

def forget_WSC(hdt:HDTDocument, rule_list:list, search_space:set, alpha=0.3, beta = 0.7, ratio=0.95):
    forget_triples = dict()
    rule_triples = get_all_triples_from_rule_list(rule_list)
    # predicate_graph_dict = construct_graph_dict_from_hdt(hdt)
    g = nx.Graph()
    dig = nx.DiGraph()
    triples, _ = hdt.search((None, None, None))
    for s, p, o in triples:
        sub = str(s).replace("http://example.org/","")
        pre = str(p).replace("http://example.org/","")
        obj = str(o).replace("http://example.org/","")
        g.add_edge(sub,obj)
        dig.add_edge(sub,pre)
        dig.add_edge(pre,obj)
    PPR_dicts = {}
    predicate_dict = get_predicate_degree_centrality(dig)
    target_set = get_all_targets_from_rule_list(rule_list)
    if os.path.exists("forget_data/PPR_dicts.pickle"):
        with open("forget_data/PPR_dicts.pickle", "rb") as f:
            PPR_dicts = pickle.load(f)
    else:
        for target in tqdm(target_set,desc="building init PPR for each target"):
            PPR_dicts[target] = ppr_score(g, target)
        with open("forget_data/PPR_dicts.pickle", "wb") as f:
            pickle.dump(PPR_dicts, f)
    search_space -= rule_triples
    for triple in tqdm(search_space, desc="analysing search space with WSC impact"):
        if triple in rule_triples:
            continue
        # forget_triples[triple] = check_with_WSC(g,dig,rule_list, triple, RBS_dicts, predicate_dict, alpha, beta)
        forget_triples[triple] = check_with_WSC_PRR_simple(g,dig,rule_list, triple,PPR_dicts, predicate_dict, alpha, beta)
    # sort forget_triples from the highest to the lowest
    forget_triple_dict = sorted(forget_triples.items(), key=lambda x: x[1], reverse=True)
    # select top ratio% of the triples
    forget_triples = set([triple for triple, _ in forget_triple_dict[:int(len(forget_triple_dict)*ratio)]])

    # triple_score_dict = dict()
    # original_WSC_dict = get_WSC_cheap_scores_rules(hdt, rule_list, [], alpha, beta, rule_alpha, rule_beta)
    # # for rule in rule_list:

    # for triple in tqdm(search_space, desc="analysing search space with WSC impact"):
    #     delta_socre = 0.0
    #     forget_WSC_dict = get_WSC_cheap_scores_rules(hdt, rule_list, [triple], alpha, beta, rule_alpha, rule_beta)
    #     # delta score will be the sum of all the differences between the original and the forget WSC scores
    #     for rule in rule_list:
    #         delta_socre += forget_WSC_dict[rule] - original_WSC_dict[rule]
    #     triple_score_dict[triple] = delta_socre
    # # select the top radio% of the triples
    # sorted_dict = sorted(triple_score_dict.items(), key=lambda x: x[1], reverse=True)
    # forget_triples = set([triple for triple, _ in sorted_dict[:int(len(sorted_dict)*ratio)]])
    return forget_triples

def forget_LM_WSC(hdt:HDTDocument, rule_list:list, search_space:set, alpha=0.5, beta = 0.5, rule_alpha=0.5, rule_beta=0.5, ratio=0.95):
    LM_triples = forget_LM(rule_list, search_space)
    WSC_triples = forget_WSC(hdt, rule_list, LM_triples, alpha, beta, rule_alpha, rule_beta, ratio)
    return WSC_triples

def reverse_backward_sampling_gt(graph, target, max_hop=3, num_samples=100):
    n_vertices = graph.num_vertices()
    influence_scores = np.zeros(n_vertices)
    for _ in range(num_samples):
        current_hop = 0
        current_node = target
        while current_hop < max_hop:
            influence_scores[current_node] += 1
            predecessors = [v for v in graph.vertex(current_node).in_neighbors()]
            if not predecessors:
                break
            current_node = random.choice(predecessors).index
            current_hop += 1
    influence_scores /= num_samples
    return influence_scores

def reverse_backward_sampling_gt_to_dict(graph, target, max_hop=3, num_samples=100):
    influence_scores_array = reverse_backward_sampling_gt(graph, target, max_hop, num_samples)
    influence_scores_dict = {int(v): score for v, score in enumerate(influence_scores_array)}
    return influence_scores_dict

# def pre_compute_everything_for_forget(hdt:HDTDocument, rules:list):
#     # g = nx.Graph()
#     dig = nx.DiGraph()
#     gt = gt_all.Graph(directed=False)
#     vertex_dict = {}
#     triples, _ = hdt.search((None, None, None))
#     entities = set()
#     forget_triples = set()
#     for s, p, o in triples:
#         sub = str(s).replace("http://example.org/","")
#         pre = str(p).replace("http://example.org/","")
#         obj = str(o).replace("http://example.org/","")
#         if sub not in vertex_dict:
#             vertex_dict[sub] = gt.add_vertex()
#         if obj not in vertex_dict:
#             vertex_dict[obj] = gt.add_vertex()
#         gt.add_edge(vertex_dict[sub], vertex_dict[obj])
#         # g.add_edge(sub,obj)
#         dig.add_edge(sub,pre)
#         dig.add_edge(pre,obj)
#         entities.add(sub)
#         entities.add(obj)
#         forget_triples.add(f"{pre}({sub},{obj})")
#     RBS_dicts = {}
#     predicate_dicts = {}
#     predicate_dicts["init"] = get_predicate_degree_centrality(dig)
#     RBS_dict = {}
#     for rule in tqdm(rules,desc="foreach rule"):
#         head = rule.split(" <= ")[0]
#         source, _, target = get_s_p_o(head)
#         target_vertex = vertex_dict[target]
#         gt_RBS = reverse_backward_sampling_gt_to_dict(gt, int(target_vertex))
#         RBS = {k: gt_RBS[int(vertex_dict[k])] for k in vertex_dict.keys()}
#         RBS_dict[target] = RBS
#     RBS_dicts["init"] = RBS_dict
#     print(RBS_dicts)

#     for triple in tqdm(forget_triples, desc="foreach triple"):
#         s, p, o = get_s_p_o(triple)
#         # g.remove_edge(s,o)
#         gt.remove_edge(vertex_dict[s], vertex_dict[o])
#         dig.remove_edge(s,p)
#         dig.remove_edge(p,o)
#         predicate_dicts[triple] = get_predicate_degree_centrality(dig)
#         RBS_dict = {}
#         for rule in rules:
#             head = rule.split(" <= ")[0]
#             source, _, target = get_s_p_o(head)
#             target_vertex = vertex_dict[target]
#             gt_RBS = reverse_backward_sampling_gt_to_dict(gt, int(target_vertex))
#             RBS = {k: gt_RBS[int(vertex_dict[k])] for k in vertex_dict.keys()}
#             RBS_dict[target] = RBS
#         RBS_dicts[triple] = RBS_dict
#         # g.add_edge(s,o)
#         gt.add_edge(vertex_dict[s], vertex_dict[o])
#         dig.add_edge(s,p)
#         dig.add_edge(p,o)
#     with open("forget_data/RBS_dicts.pickle", "wb") as f:
#         pickle.dump(RBS_dicts, f)
#     with open("forget_data/predicate_dicts.pickle", "wb") as f:
#         pickle.dump(predicate_dicts, f)

def save_triples(triples:set, path:str):
    with open(path, "w") as f:
        for triple in triples:
            f.write(f"{triple[0]},{triple[1]},{triple[2]}\n")
    return
