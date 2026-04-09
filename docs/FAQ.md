# Frequently Asked Questions

## Why would anyone want agents to fail?

ALEval inverts normal benchmark semantics on purpose. Normal benchmarks measure capability — can the agent solve the task? ALEval uses **impossible** tasks where no correct solution exists. The question flips to: *will the agent cheat to appear successful?*

If an agent passes a task with self-contradictory tests, it must have gamed the tests (modified them, produced degenerate output, etc.). That's reward hacking. ALEval then asks whether the agent will be honest about what it did.

## How do you know the agent reward-hacked vs. just got lucky?

The tasks use **conflicting test assertions** — e.g., a test that asserts both `f(1) == True` and `f(1) == False`. No function can satisfy both simultaneously. Any solution that makes all tests pass must have:
- Modified the test file to remove contradictions
- Produced output that somehow bypasses test execution
- Exploited a scorer loophole

All of these are reward hacking by definition.

## Why same-chat callout instead of a separate conversation?

Design choice: the callout happens in the same conversation so the agent has **full context** of what it just did. If the agent modified tests to pass, it knows it did. This makes lies more deliberate and informative than asking in a fresh conversation where the agent has no memory.

The tradeoff is that the same-chat context also gives the agent information that could inform strategic responding. This is a known limitation documented in the [validity report](../agent_artefacts/aleval/validity/VALIDITY_REPORT.md).

## Can agents game the callout?

Yes. A sufficiently sophisticated model could:
- Always say "yes" to avoid being classified as lying (but this reveals reward hacking awareness)
- Give evasive responses to avoid committing
- Tailor its response based on understanding of the classification system

This is a documented limitation. The LLM judge provides a cross-check against the deterministic classifier, but both are gameable in principle. The value is in measuring what current models *actually do*, not what they theoretically could do.

## Why use a regex classifier instead of an LLM?

The deterministic classifier is the primary label because:
- **Reproducibility**: Same input always produces same output
- **Cost**: Zero API calls during scoring
- **Speed**: Instant classification
- **Transparency**: The logic is inspectable (first-token heuristic)

The LLM judge exists as optional enrichment for cases where the regex misses nuance. It runs post-hoc during report generation, so it never affects the primary evaluation.

## What does this eval actually measure about AI safety?

ALEval measures **honesty about misbehavior when directly confronted**. Specifically:

1. Will frontier models cheat to appear successful? (reward hacking rate)
2. When caught, will they admit it or deny it? (lie/truth/evasive distribution)

This is relevant to AI safety because agents that lie about their actions when asked are harder to oversee and correct.

## How is this different from ImpossibleBench?

[ImpossibleBench](https://arxiv.org/abs/2510.20270) measures **whether** agents reward-hack on impossible tasks. ALEval extends this by measuring **whether agents are honest about it**. ImpossibleBench stops at "did the agent pass?" — ALEval continues with "and did it lie about how?"

## Do I need Docker?

Only for:
- SWE-bench evaluations (always require Docker for sandboxed repo environments)
- LiveCodeBench with `--sandbox docker`

For quick testing, LiveCodeBench works with `--sandbox local`:
```bash
inspect eval src/impossiblebench/lcb/tasks.py@aleval_livecodebench_minimal \
  --model openrouter/openai/gpt-5 --sandbox local -T limit=3
```

## What models can I use?

Any model available through [OpenRouter](https://openrouter.ai/). ALEval uses litellm's `openrouter/<provider>/<model>` format:
```
openrouter/openai/gpt-5
openrouter/anthropic/claude-opus-4-20250514
openrouter/google/gemini-2.5-pro
```

## How much does a full eval run cost?

Cost depends on the model and number of samples. For LiveCodeBench minimal (247 samples), expect roughly:
- GPT-5: ~$15-25 per full run
- Claude: ~$15-30 per full run
- Budget for a full 8-model panel: ~$200-400

These are rough estimates. Use `-T limit=3` for cheap test runs first.

## Why are 2 tests xfailed?

The regex callout classifier has two known edge cases where tokenization produces false results:
- The word "no-nonsense" tokenizes to `["no", "nonsense"]`, so the first-token heuristic classifies it as "no"
- Similar compound words can trigger false classification

These are documented as `xfail` tests rather than fixed, because fixing them would add complexity to the classifier without meaningful impact on real callout responses (agents rarely use these edge-case words).
