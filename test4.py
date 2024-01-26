import pandas as pd
import re
from collections import defaultdict

graph = defaultdict(list)

pattern = re.compile(r"(user \d+|movie \d+|category \d+)( watched| belong_to)?")


file = pd.read_csv('best_pred_paths.csv', delimiter=',',header = 0)

for index, row in file.iterrows():
    path = row['path']
    print(path.replace("\t","\\t"))