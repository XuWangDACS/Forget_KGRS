from rdflib import Graph, URIRef
import numpy as np

def initialize_particles(graph, query_uris, num_particles=1000):
    particles = {str(node): 0 for node in graph.all_nodes()}
    for uri in query_uris:
        particles[uri] += num_particles // len(query_uris)
    return particles

def spread_particles(graph, particles, alpha=0.85):
    new_particles = {node: 0 for node in particles.keys()}
    for node, count in particles.items():
        neighbors = list(graph.objects(URIRef(node), None))
        if neighbors:
            spread_count = (1 - alpha) * count
            keep_count = alpha * count
            new_particles[node] += keep_count
            for neighbor in neighbors:
                new_particles[str(neighbor)] += spread_count / len(neighbors)
        else:
            new_particles[node] += count
    return new_particles

def personalized_pagerank(graph, query_uris, iterations=10):
    particles = initialize_particles(graph, query_uris)
    for _ in range(iterations):
        particles = spread_particles(graph, particles)
    return sorted(particles.items(), key=lambda x: x[1], reverse=True)

# Example usage with a simple RDF graph
g = Graph()
g.add((URIRef("http://example.org/1"), URIRef("http://example.org/relatedTo"), URIRef("http://example.org/2")))
g.add((URIRef("http://example.org/2"), URIRef("http://example.org/relatedTo"), URIRef("http://example.org/3")))
query_uris = ["http://example.org/1"]
ranked_uris = personalized_pagerank(g, query_uris)
print(ranked_uris)
