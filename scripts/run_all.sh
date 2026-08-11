#!/usr/bin/env bash
set -e

python -m rag.ingest --path data/docs
python -m evaluation.rag_eval --k 5
python -m evaluation.rag_answer_eval --k 5
python -m evaluation.cost_model
python -m judge.run

echo "Done. See results/"
