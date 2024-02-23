
from __future__ import absolute_import, division, print_function
import os
import pickle
import gzip
import argparse
import re
from utils import *
from data_utils import AmazonDataset
from knowledge_graph import KnowledgeGraph
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

def split_entity(s:str):
    match = re.match(r"([^\d]+)(\d+)", s)
    non_number, number = match.groups()
    return non_number, int(number)

def generate_labels(dataset, mode='train'):
    review_file = '{}/{}.txt.gz'.format(DATASET_DIR[dataset], mode)
    user_products = {}  # {uid: [pid,...], ...}
    id2kgid = get_product_id_kgid_mapping(dataset)
    uid2kg_uid = get_uid_to_kgid_mapping(dataset)
    with gzip.open(review_file, 'r') as f:
        for line in f:
            line = line.decode('utf-8').strip()
            arr = line.split(' ')
            user_idx = uid2kg_uid[int(arr[0])]
            product_idx = int(arr[1])
            if product_idx not in id2kgid: continue
            if user_idx not in user_products:
                user_products[user_idx] = []
            user_products[user_idx].append(id2kgid[product_idx])
    save_labels(dataset, user_products, mode=mode)

def forget_rebuildKG(kg: KnowledgeGraph, path: str)->KnowledgeGraph:
    with open(path, 'r') as f:
        for line in f:
            s, p, o = line.strip().split(",")
            stype, sid = split_entity(s)
            otype, oid = split_entity(o)
            kg._remove_edge(stype, sid, p, otype, oid)
    return kg

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default=ML1M, help='ML1M')
    parser.add_argument('--path', type=str,required=True, help='path to the file containing the triples to remove')
    args = parser.parse_args()
    print('ReCreate', args.dataset, 'knowledge graph from dataset...')
    dataset = load_dataset(args.dataset)
    dataset.dataset_name = "ml1m"
    kg = KnowledgeGraph(dataset)
    kg = forget_rebuildKG(kg, args.path)
    kg.compute_degrees()
    save_kg(args.dataset, kg)
    print('ReGenerate', args.dataset, 'train/test labels.')
    generate_labels(args.dataset, 'train')
    generate_labels(args.dataset, 'test')
