from elliot.run import run_experiment
from config_template import TEMPLATE
import os
import argparse
import pandas as pd

config_dir = 'config_files/'
RANDOM_SEED = 42

parser = argparse.ArgumentParser()

parser.add_argument('--dataset', required=True, type=str, nargs='+')
parser.add_argument('--start', required=False, type=int)
parser.add_argument('--end', required=False, type=int)

args = parser.parse_args()

datasets = args.dataset
start = args.start
end = args.end

# # check if datasets exist
# for dataset in datasets:
#     for sub in range(start, end):
#         data = os.path.exists(f'../data/{dataset}/{sub}/MovieLens1M_g{sub}.tsv')
#         if not data:
#             raise FileNotFoundError(f'Missing dataset for {dataset} at sub {sub}')

# run experiments on each generated dataset
for dataset in datasets:
    for sub in range(start, end):
        df = pd.read_csv(f'./data/{dataset}/{sub}/dataset_filtered_ordered_g{sub}.tsv', sep="\t", header=None)
        max_users = (df[0].nunique())*0.5
        max_items = (df[1].nunique())*0.5
        config = TEMPLATE.format(dataset=dataset, sub=sub, max_users=max_users, max_items=max_items)
        config_path = os.path.join(config_dir, 'runtime_conf.yml')
        with open(config_path, 'w') as file:
            file.write(config)
        print()
        run_experiment(config_path)


