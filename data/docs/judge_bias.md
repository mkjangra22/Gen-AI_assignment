# LLM Judge Bias Controls

Pairwise evaluation can be affected by position bias: a judge may prefer the first candidate. The mitigation is to run every pair in both A-B and B-A order and report the flip rate.

Verbosity bias occurs when a judge rewards longer answers. The rubric explicitly says not to reward length by itself and includes a verbose-but-wrong probe.

Self-enhancement bias occurs when a judge prefers outputs from its own model family. The generator and judge are independently configurable, so a different model family can be used for the judge.

Sycophancy and style bias are reduced by requiring per-criterion evidence and including confidently-wrong adversarial outputs.

Absolute score clustering is reduced by anchored 1/3/5 rubric descriptions and pairwise winner decisions.

Judge validation should include agreement with gold labels, test-retest consistency, and adversarial probes such as verbose-but-wrong and terse-but-correct answers.
