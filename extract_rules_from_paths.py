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



# Regular expression to capture entities and any relations between them
pattern = re.compile(r"(\buser \d+|\bmovie \d+|\bcategory \d+|\bproducer \d+|\bwritter \d+|\bactor \d+|\bdirector \d+|\beditor \d+|\bcinematographer \d+|\bproduction_company \d+)( [\w_]+)?")

# Function to extract entities and relations from each line
def extract_from_line(line):
    triples_tsv = []
    triples = []
    triple_path = set()
    matches = pattern.findall(line)
    for i in range(len(matches) - 1):
        entity1, relation = matches[i]
        entity2, _ = matches[i + 1]
        if relation:
            domain_type = relation_domain_range_dict[relation.strip()][0]
            range_type = relation_domain_range_dict[relation.strip()][1]
            if entity1.startswith(domain_type) and entity2.startswith(range_type):
                subject = entity1.split(" ")[0]+entity1.split(" ")[1]
                subject1 = entity1.split(" ")[0]
                subject2= entity1.split(" ")[1]
                object = entity2.split(" ")[0]+entity2.split(" ")[1]
                object1 = entity2.split(" ")[0]
                object2 = entity2.split(" ")[1]
                triples.append(f"{relation.strip()}({subject},{object})")
                triples_tsv.append(f"{subject1}\t{subject2}\t{relation.strip()}\t{object1}\t{object2}")
                triple_path.add(subject)
                triple_path.add(object)
            else:
                subject = entity2.split(" ")[0]+entity2.split(" ")[1]
                subject1 = entity2.split(" ")[0]
                subject2 = entity2.split(" ")[1]
                object = entity1.split(" ")[0]+entity1.split(" ")[1]
                object1 = entity1.split(" ")[0]
                object2 = entity1.split(" ")[1]
                triples.append(f"{relation.strip()}({subject},{object})")
                triples_tsv.append(f"{subject1}\t{subject2}\t{relation.strip()}\t{object1}\t{object2}")
                triple_path.add(subject)
                triple_path.add(object)
    return triples,triples_tsv, triple_path

file1 = pd.read_csv('pre_data/uid_pid_explanation_exp1.csv', delimiter=',',header = 0)
# Process each line separately
for index, row in file1.iterrows():
    path = row['path']
    body,body_tsv, tpath = extract_from_line(path)
    body_t = '\t'.join(body_tsv)
    rule_tsv = f"user\t{row['uid']}\trecommend\tmovie\t{row['pid']}\t<=\t{body_t}"  # Join the body with spaces
    rule = f"recommend(user{row['uid']},movie{row['pid']}) <= {' & '.join(body)}"  # Join the body with spaces
    tpath = '\t'.join(tpath)
    rule_path = f"user{row['uid']}\tmovie{row['pid']}\t{tpath}"
    with open("exp_data/rules_exp1.txt", "a+") as f:
        f.write(rule + "\n")
    with open("exp_data/rules_exp1.tsv", "a+") as f:
        f.write(rule_tsv + "\n")
    with open("exp_data/paths_exp1.txt", "a+") as f:
        f.write(rule_path + "\n")
        
file2 = pd.read_csv('pre_data/uid_pid_explanation_exp2.csv', delimiter=',',header = 0)
# Process each line separately
for index, row in file1.iterrows():
    path = row['path']
    body,body_tsv,tpath = extract_from_line(path)
    body_t = '\t'.join(body_tsv)
    rule_tsv = f"user\t{row['uid']}\trecommend\tmovie\t{row['pid']}\t<=\t{body_t}"  # Join the body with spaces
    rule = f"recommend(user{row['uid']},movie{row['pid']}) <= {' & '.join(body)}"  # Join the body with spaces
    tpath = '\t'.join(tpath)
    rule_path = f"user{row['uid']}\tmovie{row['pid']}\t{tpath}"
    with open("exp_data/rules_exp2.txt", "a+") as f:
        f.write(rule + "\n")
    with open("exp_data/rules_exp2.tsv", "a+") as f:
        f.write(rule_tsv + "\n")
    with open("exp_data/paths_exp2.txt", "a+") as f:
        f.write(rule_path + "\n")
