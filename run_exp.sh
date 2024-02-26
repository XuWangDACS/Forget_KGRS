#!/bin/sh

echo "Running experiment..."
echo "---------------------"
echo "creating KG and train & test labels..."
/home/xu-wang/miniconda3/envs/kdd/bin/python preprocess.py
echo "---------------------"
echo "TransE embedding training..."
/home/xu-wang/miniconda3/envs/kdd/bin/python train_transe_model.py
echo "---------------------"
echo "train agent..."
/home/xu-wang/miniconda3/envs/kdd/bin/python train_agent.py
echo "---------------------"
echo "test agent to get predicted paths..."
/home/xu-wang/miniconda3/envs/kdd/bin/python test_agent.py
echo "---------------------"
echo "getting results and metrics..."
/home/xu-wang/miniconda3/envs/kdd/bin/python main.py --result_dir=original_results
echo "---------------------"

echo "Now start forgetting"
echo "---------------------"
echo "cleaning agent and transe model..."
mv tmp/ml1m/train_agent tmp/ml1m/train_agent_original
cd tmp/ml1m/train_agent
rm -f *
cd ..
mv train_transe_model train_transe_model_original
cd ../train_transe_model
rm -f *
cd ../../..

echo "---------------------"
echo "forgetting..."
/home/xu-wang/miniconda3/envs/kdd/bin/python forget_main.py
