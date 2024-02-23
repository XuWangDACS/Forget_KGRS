#!/bin/sh

echo "Running experiment..."
echo "---------------------"
echo "creating KG and train & test labels..."
python3 preprocess.py
echo "---------------------"
echo "TransE embedding training..."
python3 train_transe_model.py
echo "---------------------"
echo "train agent..."
python3 train_agent.py
echo "---------------------"
echo "test agent to get predicted paths..."
python3 test_agent.py
echo "---------------------"
echo "getting results and metrics..."
python3 main.py --dateset=ml1m --result_dir=original_results
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
python3 forget_main.py
