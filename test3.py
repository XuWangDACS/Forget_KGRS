import networkx as nx
import numpy as np
import random

def RBS(G, target, alpha, theta, lambda_function):
    V = list(G.nodes())  # List of nodes in the graph
    L = int(np.log(1/theta) / np.log(1/alpha))  # Maximum number of hops
    estimates = np.zeros((L+1, len(V)))  # PPR estimates for each node at each level
    estimates[0, V.index(target)] = alpha  # Initial probability for the target node

    for l in range(L):  # Iterate over levels
        for node in V:
            if estimates[l, V.index(node)] > 0:  # If there's a non-zero estimate
                for u in G.neighbors(node):  # Iterate over neighbors (acting as in-neighbors)
                    dout_u = G.degree(u)  # Degree of u (acting as dout)
                    if dout_u <= lambda_function(u) * (1-alpha) * estimates[l, V.index(node)] / alpha / theta:
                        estimates[l+1, V.index(u)] += (1-alpha) * estimates[l, V.index(node)] / dout_u
                    else:
                        r = random.random()
                        if r < alpha * theta / lambda_function(u):
                            estimates[l+1, V.index(u)] += alpha * theta / lambda_function(u)

    # Sum up estimates from all levels for each node
    final_estimates = np.sum(estimates, axis=0)
    return dict(zip(V, final_estimates))

# Define your graph
G = nx.DiGraph()
G.add_nodes_from(["John", "Mary", "Jill", "Todd", "iPhone5", "Kindle Fire", "Fitbit Flex Wireless", "Harry Potter", "Hobbit"])
G.add_edges_from([
    ("John", "iPhone5"),
    ("John", "Kindle Fire"),
    ("Mary", "iPhone5"),
    ("Mary", "Kindle Fire"),
    ("Mary", "Fitbit Flex Wireless"),
    ("Jill", "iPhone5"),
    ("Jill", "Kindle Fire"),
    ("Jill", "Fitbit Flex Wireless"),
    ("Todd", "Fitbit Flex Wireless"),
    ("Todd", "Harry Potter"),
    ("Todd", "Hobbit"),
])

# Example usage
target = "John"  # Target node
alpha = 0.15  # Teleport probability
theta = 0.1  # Error parameter
lambda_function = lambda u: G.degree(u)  # Lambda function based on node degree
ppr_estimates = RBS(G, target, alpha, theta, lambda_function)

# Print the PPR estimates
for node, value in ppr_estimates.items():
    print(f"{node}: {value}")