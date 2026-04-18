# Frequently Asked Questions

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

Cost depends on the model and number of samples. For LiveCodeBench minimal (106 samples), expect roughly:

- GPT-5: ~$15-25 per full run
- Claude: ~$15-30 per full run
- Budget for a full 8-model panel: ~$200-400

These are rough estimates. Use `-T limit=3` for cheap test runs first.

## Why are 2 tests xfailed?

The regex callout classifier has two known edge cases where tokenization produces false results:

- The word "no-nonsense" tokenizes to `["no", "nonsense"]`, so the first-token heuristic classifies it as "no"
- Similar compound words can trigger false classification

These are documented as `xfail` tests rather than fixed, because fixing them would add complexity to the classifier without meaningful impact on real callout responses (agents rarely use these edge-case words).