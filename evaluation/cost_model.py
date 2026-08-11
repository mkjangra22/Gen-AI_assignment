import csv
from pathlib import Path

# Transparent assignment assumptions.
# Update these numbers for your actual deployment before submission.
VECTOR_DB_LOCAL_MONTHLY = 8.0  # USD: small VM / disk budget assumption
PINECONE_BUILDER_MONTHLY_MIN = 20.0  # current public Builder tier minimum
AVG_METADATA_KB = 1.0
DIMENSIONS = 384

# Query/generation assumptions:
QUERIES_PER_MONTH = 100_000
AVG_INPUT_TOKENS = 900
AVG_OUTPUT_TOKENS = 180

# Illustrative LLM price assumptions, not hard-coded vendor claims.
INPUT_PRICE_PER_1M = 0.15
OUTPUT_PRICE_PER_1M = 0.60

def llm_monthly():
    return (
        QUERIES_PER_MONTH * AVG_INPUT_TOKENS / 1_000_000 * INPUT_PRICE_PER_1M
        + QUERIES_PER_MONTH * AVG_OUTPUT_TOKENS / 1_000_000 * OUTPUT_PRICE_PER_1M
    )

def local_cost(vectors):
    # Local store cost model: fixed small compute/storage budget.
    return VECTOR_DB_LOCAL_MONTHLY + llm_monthly()

def managed_cost(vectors):
    # Pinecone Builder starts at $20/month according to the current public pricing.
    # Actual usage charges can increase with reads/writes/storage.
    return PINECONE_BUILDER_MONTHLY_MIN + llm_monthly()

def main():
    rows = []
    for vectors in [100_000, 1_000_000, 10_000_000]:
        rows.append({
            "vectors": vectors,
            "dimensions": DIMENSIONS,
            "metadata_kb_per_vector": AVG_METADATA_KB,
            "local_embedded_assumption_usd_month": round(local_cost(vectors), 2),
            "managed_pinecone_builder_floor_usd_month": round(managed_cost(vectors), 2),
            "note": (
                "Local figure assumes fixed small VM/storage budget; "
                "managed figure is a pricing-floor comparison, not a quote. "
                "Actual managed usage depends on reads/writes/storage."
            ),
        })

    Path("results").mkdir(exist_ok=True)
    with open("results/cost_comparison.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(row)

if __name__ == "__main__":
    main()
