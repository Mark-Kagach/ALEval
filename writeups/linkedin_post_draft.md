# LinkedIn Draft

Shipped a major upgrade to our ImpossibleBench ALEval workflow:

- Full support for LiveCodeBench + SWE-bench
- Both minimal and tools scaffolds
- Deterministic same-chat callout labels (`lie`, `truth`, `evasive`) attached to Inspect logs
- Campaign tooling for multi-model runs + reproducible artifact export

The key design choice: we only evaluate callout honesty in trajectories where the agent already succeeded on the benchmark task. That keeps the measurement action-grounded, rather than purely self-reported.

Next step is publishing comparative results across a balanced model panel with split-wise and scaffold-wise breakdowns.

If you want the write-up and reproducibility pack when it is finalized, comment “interested” and I’ll share it.
