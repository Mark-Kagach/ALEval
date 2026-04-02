# X / Twitter Thread Draft

1/ We upgraded ImpossibleBench ALEval to measure both coding-task behavior and same-chat honesty after success.

2/ Scope now covers:
- LiveCodeBench + SWE-bench
- minimal + tools scaffolds
- original / oneoff / conflicting splits

3/ Key metric split:
- benchmark outcome (`C`/`I`)
- callout label among passes: `lie`, `truth`, `evasive`

4/ Why this matters: post-hoc “did you cheat?” without behavior context is weak. We condition honesty checks on concrete successful actions.

5/ We also added reproducible campaign tooling:
- manifest-driven runs
- command export
- sample-level + aggregate artifact export

6/ Full report (mini-paper + LessWrong write-up) coming next with model-by-model comparisons.
