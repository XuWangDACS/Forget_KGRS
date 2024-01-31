import numpy as np
import random

def RBS(G, target, alpha, theta, lambda_function):
    """RBS algorithm for computing PPR estimates (RBS paper doi: 10.1145/3394486.3403108)
    G: Graph (DiGraph or Graph in nx)
    target: Target node
    alpha: Teleport probability
    theta: Error parameter
    lambda_function: Lambda function based on node degree
    
    Returns: Dictionary of PPR estimates
    """
    V = list(G.nodes())
    L = int(np.log(1/theta) / np.log(1/alpha))
    estimates = np.zeros((L+1, len(V)))
    estimates[0, V.index(target)] = alpha

    for l in range(L):
        for node in V:
            if estimates[l, V.index(node)] > 0:
                for u in G.neighbors(node):
                    dout_u = G.degree(u)
                    if dout_u <= lambda_function(u) * (1-alpha) * estimates[l, V.index(node)] / alpha / theta:
                        estimates[l+1, V.index(u)] += (1-alpha) * estimates[l, V.index(node)] / dout_u
                    else:
                        r = random.random()
                        if r < alpha * theta / lambda_function(u):
                            estimates[l+1, V.index(u)] += alpha * theta / lambda_function(u)

    # Sum up estimates from all levels for each node
    final_estimates = np.sum(estimates, axis=0)
    return {key: value for key, value in dict(zip(V, final_estimates)).items() if value != 0}

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