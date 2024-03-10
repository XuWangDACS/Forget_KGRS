#!/bin/sh

echo "Running original experiment..."
python preprocess.py
python train_transe_model.py
python train_agent.py
python test_agent.py
python main.py --result_dir=original_results
echo "Results stored in original_results"
echo "---------------------"

echo "cleaning temporary files..."
cd datasets/train_agent
rm -f *
cd ../..
cd datasets/train_transe_model
rm -f *
cd ../..

echo "---------------------"
echo "forgetting..."
python forget_main.py
echo "Forget triples stored in forget_data/iforget_LM_triples.txt and forget_data/iforget_WSC_triples.txt"

echo "---------------------"
echo "rebuild knowledge graph and re-experiment... (Least Model forgetting)"
python Forget_rebuildKG.py --path=forget_data/iforget_LM_triples.txt
python train_transe_model.py
python train_agent.py
python test_agent.py
python main.py --result_dir=iforget_LM_results
echo "Results stored in iforget_LM_results"

echo "---------------------"
echo "cleaning temporary files..."
cd datasets/train_agent
rm -f *
cd ../..
cd datasets/train_transe_model
rm -f *
cd ../..

echo "---------------------"
echo "rebuild knowledge graph and re-experiment... (Weakest Sufficient Condition forgetting)"
python Forget_rebuildKG.py --path=forget_data/iforget_WSC_triples.txt
python train_transe_model.py
python train_agent.py
python test_agent.py
python main.py --result_dir=iforget_WSC_results
echo "Results stored in iforget_WSC_results"

echo "---------------------"
echo "cleaning temporary files..."
cd datasets/train_agent
rm -f *
cd ../..
cd datasets/train_transe_model
rm -f *
cd ../..

echo "Done!"