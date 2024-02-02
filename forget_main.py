import argparse
from rdflib import Graph, Namespace
from rdflib_hdt import HDTStore, optimize_sparql, HDTDocument
import os
from forget_functions import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--hdt', type=str, default="forget_data/KnowlegeGraph.hdt", help='HDT file path.')
    parser.add_argument('--rule', type=str, default="pre_data/uid_pid_explanation_exp2.csv", help='Path to the file containing passive forgetting rules.')
    parser.add_argument('--forget_type', type=str, default="pforget", help='Type of forgetting (pforget or iforget, represent passive forget or intentional forget).')
    parser.add_argument('--random_forget_rule', type=bool, default=False, help='randomly forget one rule. (test passive forgetting)')
    parser.add_argument('--random_forget_triple', type=bool, default=False, help='randomly forget one triple. (test passive forgetting)')
    parser.add_argument('--pforget_rule', type=str, default="forget_data/forget_rules.txt", help='path to the file containing passive forgetting rules. (passive forgetting)')
    
    args = parser.parse_args()
    
    assert args.forget_type=="pforget" and os.path.isfile(args.passive_forget), f"{args.passive_forget} is not a valid file path (provide valid forget rules in forget_data/forget_rules.txt)."
    assert os.path.isfile(args.hdt), f"{args.hdt} is not a valid file path."
    
    hdt = HDTDocument(args.hdt) # Load an HDT file. Missing index file will be generated
    rule_list = parse_rules(args.rule)
    
    if args.forget_type == "pforget":
        if args.random_forget_rule:
            rule_list = random_forget_rule(rule_list)
        if args.random_forget_triple:
            rule_list = random_forget_triple(rule_list)
        search_space = build_pforget_search_space(rule_list)
        forget(hdt, search_space)
    elif args.forget_type == "iforget":
        forget(hdt, rule_list)
        
    
    