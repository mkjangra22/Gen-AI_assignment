# Submission Checklist

- [ ] `pip install -r requirements.txt`
- [ ] Configure `.env`
- [ ] `python -m rag.ingest --path data/docs`
- [ ] Verify re-ingest does not increase collection count (record before/after)
- [ ] Start FastAPI and test `/health` + `/query`
- [ ] Run `python -m evaluation.rag_eval --k 5`
- [ ] Run `python -m evaluation.cost_model`
- [ ] Configure judge model from a different family than generator if possible
- [ ] Run `python -m judge.run`
- [ ] Inspect `results/`
- [ ] Run `pytest`
- [ ] Add a short Git history with logical commits
- [ ] Replace illustrative cost assumptions with the exact assumptions you want to defend in the interview/submission
- [ ] Do not commit `.env` or API keys
