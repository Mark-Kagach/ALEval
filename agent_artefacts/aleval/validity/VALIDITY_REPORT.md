# ALEval Evaluation Validity Report

## Name Validity

**Assessment: PASS with caveat**

"ALEval" (Action-Lying Evaluation) accurately represents what is measured:
the evaluation measures whether agents *lie about* reward hacking after being
caught, not whether they reward-hack per se (which is measured by the underlying
ImpossibleBench pass rate).

The name could be misread as measuring general lying ability. The full name
"Action-Lying Evaluation of Reward-Hacking LLMs" clarifies the scope.

**Recommendation**: The eval.yaml description makes the behavioral measurement
clear. No name change required.

## Dataset Validity

**Assessment: PASS with intentional inversion**

ALEval deliberately inverts normal dataset validity assumptions:

- **Can a model succeed?** — Not legitimately. Tasks use conflicting test splits
  that are self-contradictory by design. A "pass" indicates reward hacking.
- **Can a model fail?** — Yes, by either failing to solve the task or by
  admitting reward hacking when asked.
- **Submission mechanism** — Clear: agents submit code via sandbox execution
  for LCB, or file modifications for SWE-bench.

This intentional impossibility is the core measurement mechanism and is
well-documented in the README, eval.yaml description, and the original
ImpossibleBench paper (arXiv:2510.20270).

## Scoring Validity

**Assessment: PARTIAL — known limitations documented**

- **Task completion scoring** — Binary (pass/fail) based on actual test
  execution in sandbox. This measures genuine reward hacking behavior.
- **Callout classification** — Uses regex matching on natural language, which
  is a proxy for honesty. Known limitations:
  - 1 xfail test documents a misclassification edge case
  - The regex may miss nuanced evasions
- **LLM judge** — Optional post-hoc second opinion. Not yet meta-validated
  against a labeled corpus.
- **Gameability** — A model that always says "yes" scores 100% truth. This is
  by design (honest models should admit reward hacking).

**Recommendation**: Add meta-validation against ~50 labeled responses before
publication. The xfail test serves as partial documentation.
