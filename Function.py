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
    return dict(zip(V, final_estimates))