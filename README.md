# Forget_KGRS

The code for paper "Forgetting in Knowledge Graph based Recommender Systems"

## Reproduce the experiments

First step is to install all dependency. We suggest to install python environment on conda.

`conda create -n forget python=3.9` and then run `conda activate forget`

After that, you can install dependencies by running `pip install -r requirements.txt`

Easiest way to reproduce the expeirments in the paper `sh run_exp.sh`

All the results could be found at three folder `original_results`, `iforget_LM_results`, and `iforget_WSC_results`.