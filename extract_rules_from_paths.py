import re
import pandas as pd

relations_set = {'starring', 'produced_by_producer', 'directed_by', 'edited_by', 'cinematography', 'wrote_by', 'belong_to', 'watched', 'produced_by_company'}

relation_domain_range_dict = {
    'starring': ('movie', 'actor'),
    'produced_by_producer': ('movie', 'producer'),
    'directed_by': ('movie', 'director'),
    'edited_by': ('movie', 'editor'),
    'cinematography': ('movie', 'cinematographer'),
    'wrote_by': ('movie', 'writter'),
    'belong_to': ('movie', 'category'),
    'watched': ('user', 'movie'),
    'produced_by_company': ('producer', 'production_company')
}

file = pd.read_csv('best_pred_paths.csv', delimiter=',',header = 0)

# Regular expression to capture entities and any relations between them
pattern = re.compile(r"(\buser \d+|\bmovie \d+|\bcategory \d+|\bproducer \d+|\bwritter \d+|\bactor \d+|\bdirector \d+|\beditor \d+|\bcinematographer \d+|\bproduction_company \d+)( [\w_]+)?")

# Function to extract entities and relations from each line
def extract_from_line(line):
    triples = []
    matches = pattern.findall(line)
    for i in range(len(matches) - 1):
        entity1, relation = matches[i]
        entity2, _ = matches[i + 1]
        if relation:
            domain_type = relation_domain_range_dict[relation.strip()][0]
            range_type = relation_domain_range_dict[relation.strip()][1]
            if entity1.startswith(domain_type) and entity2.startswith(range_type):
                subject = entity1.split(" ")[0]+entity1.split(" ")[1]
                object = entity2.split(" ")[0]+entity2.split(" ")[1]
                triples.append(f"{relation.strip()}({subject},{object})")
            else:
                subject = entity2.split(" ")[0]+entity2.split(" ")[1]
                object = entity1.split(" ")[0]+entity1.split(" ")[1]
                triples.append(f"{relation.strip()}({subject},{object})")
    return triples

# Process each line separately
for index, row in file.iterrows():
    path = row['path']
    body = extract_from_line(path)
    rule = f"recommend(user{row['uid']},movie{row['rec item']}) <= {' & '.join(body)}"  # Join the body with spaces
    with open("rules.txt", "a+") as f:
        f.write(rule + "\n")
