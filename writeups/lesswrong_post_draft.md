# Draft: Measuring Lying After Reward Hacking in Coding Agents

We extended ImpossibleBench to evaluate not only whether coding agents exploit impossible tests, but also what they say when asked directly in the same chat after successful completion.

## Why this matters
- Reward hacking is now frequently observed in coding-agent workflows.
- A direct “did you reward hack?” question alone is weak.
- We use action-grounded conditioning: only label honesty after concrete successful behavior.

## Setup
- Benchmarks: Impossible-LiveCodeBench and Impossible-SWEbench.
- Splits: original, oneoff, conflicting.
- Scaffolds: minimal and tools.
- Labels among passed runs: lie / truth / evasive (deterministic from first yes/no signal).

## Main results
- [Insert compact results table]
- [Insert pass-rate vs lie-rate figure]
- [Insert scaffold comparison figure]

## What surprised us
- [Model-specific behavior notes]
- [Split differences]

## Caveats
- Label is still a proxy for internal belief.
- Scaffolding and test access can change incentives substantially.

## Reproducibility
- Repo:
- Commands:
- Model versions:
- Logs/artifacts:

## Closing
The practical takeaway is that alignment checks should couple behavior with post-action communication checks, not treat either in isolation.
