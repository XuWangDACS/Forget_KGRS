import re
import pandas as pd

relations_set = {'starring', 'produced_by_producer', 'directed_by', 'edited_by', 'cinematography', 'wrote_by', 'belong_to', 'watched', 'produced_by_company'}

relation_domain_range_dict = {
    'starring': ('movie', 'actor'),
    'produced_by_producer': ('movie', 'producer'),
    'directed_by': ('movie', 'director'),
    'edited_by': ('movie', 'editor'),
    'cinematography': ('movie', 'cinematographer'),
    'wrote_by': ('movie', 'writer'),
    'belong_to': ('movie', 'category'),
    'watched': ('user', 'movie'),
    'produced_by_company': ('producer', 'company')
}

file = pd.read_csv('best_pred_paths.csv', delimiter=',',header = 0)

# Regular expression to capture entities and any relations between them
pattern = re.compile(r"(\buser \d+|\bmovie \d+|\bcategory \d+|\bproducer \d+)( [\w_]+)?")

# Function to extract entities and relations from each line
def extract_from_line(line):
    triples = []
    matches = pattern.findall(line)
    for i in range(len(matches) - 1):
        entity1, relation = matches[i]
        entity2, _ = matches[i + 1]
        if relation:  # Check if there's a relation captured
            # relations_set.add(relation.strip())  # Add the relation to the set of relations
            domain_type = relation_domain_range_dict[relation.strip()][0]
            range_type = relation_domain_range_dict[relation.strip()][1]
            if entity1.startswith(domain_type) and entity2.startswith(range_type):
                # print(f"{entity1}\t{relation.strip()}\t{entity2}")
                subject = entity1.split(" ")[1]
                object = entity2.split(" ")[1]
                triples.append(f"{relation.strip()}({subject},{object})")
            else:
                subject = entity2.split(" ")[1]
                object = entity1.split(" ")[1]
                # print(f"{entity2}\t{relation.strip()}\t{entity1}")
                triples.append(f"{relation.strip()}({subject},{object})")
            # print(f"{entity1} {relation.strip()} {entity2}")
    return triples

# Process each line separately
for index, row in file.iterrows():
    path = row['path']
    body = extract_from_line(path)
    rule = f"recommend({row['uid']},{row['rec item']}) <= {' & '.join(body)}"  # Join the body with spaces
    print(path)
    print(rule)
    print("---- Next Line ----")  # Separator for clarity

# print(relations_set)
