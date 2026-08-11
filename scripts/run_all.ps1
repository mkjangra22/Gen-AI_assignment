$ErrorActionPreference = "Stop"

python -m rag.ingest --path data/docs
python -m evaluation.rag_eval --k 5
python -m evaluation.rag_answer_eval --k 5
python -m evaluation.cost_model
python -m judge.run

Write-Host "Done. See results/."
