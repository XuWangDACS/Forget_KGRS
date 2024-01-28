import numpy as np
import random

WATCHED = 'watched'
DIRECTED_BY = 'directed_by'
PRODUCED_BY_COMPANY = 'produced_by_company'
STARRING = 'starring'
EDITED_BY = 'edited_by'
WROTE_BY = 'wrote_by'
CINEMATOGRAPHY = 'cinematography'
COMPOSED_BY = 'composed_by'
BELONG_TO = 'belong_to'
PRODUCED_BY_PRODUCER = 'produced_by_producer'
SELF_LOOP = 'self_loop'

MOVIE = 'movie'
ACTOR = 'actor'
DIRECTOR = 'director'
PRODUCTION_COMPANY = 'production_company'
EDITOR = 'editor'
WRITTER = 'writter'
CINEMATOGRAPHER = 'cinematographer'
COMPOSER = 'composer'
USER = 'user'
CATEGORY = 'category'

ML1M_TAIL_ENTITY_NAME = {0: CINEMATOGRAPHER, 1: PRODUCTION_COMPANY, 2: COMPOSER, 3: CATEGORY, 8: CATEGORY, 10: ACTOR, 14: EDITOR, 15: PRODUCER, 16: WRITTER, 18: DIRECTOR}
ML1M_RELATION_NAME = {0: CINEMATOGRAPHY, 1: PRODUCED_BY_COMPANY, 2: COMPOSED_BY, 3: BELONG_TO,  8: BELONG_TO, 10: STARRING, 14: EDITED_BY, 15: PRODUCED_BY_PRODUCER, 16: WROTE_BY, 18: DIRECTED_BY, 20: WATCHED}

ML1M = {
        0: "http://dbpedia.org/ontology/cinematography",
        1: "http://dbpedia.org/property/productionCompanies",
        2: "http://dbpedia.org/property/composer",
        3: "http://purl.org/dc/terms/subject",
        4: "http://dbpedia.org/ontology/openingFilm",
        5: "http://www.w3.org/2000/01/rdf-schema",
        6: "http://dbpedia.org/property/story",
        7: "http://dbpedia.org/ontology/series",
        8: "http://www.w3.org/1999/02/22-rdf-syntax-ns",
        9: "http://dbpedia.org/ontology/basedOn",
        10: "http://dbpedia.org/ontology/starring",
        11: "http://dbpedia.org/ontology/country",
        12: "http://dbpedia.org/ontology/wikiPageWikiLink",
        13: "http://purl.org/linguistics/gold/hypernym",
        14: "http://dbpedia.org/ontology/editing",
        15: "http://dbpedia.org/property/producers",
        16: "http://dbpedia.org/property/allWriting",
        17: "http://dbpedia.org/property/notableWork",
        18: "http://dbpedia.org/ontology/director",
        19: "http://dbpedia.org/ontology/award",
    }

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