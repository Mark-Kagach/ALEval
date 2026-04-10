# ALEval experiment report: Arena-aligned models, sample sizes, and cost estimates

This document turns the agreed LiveCodeBench-only experiment plan into a concrete briefing: which coding models to prioritize given public leaderboard signals, how many examples to run per model, and order-of-magnitude API costs. It does **not** execute evaluations.

**Scope:** LiveCodeBench impossible tasks, `split=conflicting`, presets `aleval_livecodebench_minimal` and (optionally) `aleval_livecodebench_tools`. SWE-bench is out of scope for cost reasons.

---

## 1. Leaderboard context (Code Arena, Apr 2026 snapshot)

The [Code AI Leaderboard](https://arena.ai/leaderboard/code) (Arena-style coding benchmark, **224,709 votes**, **59 models**, snapshot **Apr 1, 2026**) ranks models by Elo-style scores on **agentic coding** (multi-step reasoning and tool use). At that snapshot:


| Rank band   | Pattern (org)                                                           | Takeaway for ALEval                                                                                                                  |
| ----------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| 1–5         | **Anthropic** dominates the very top                                    | Strong candidates: **Opus / Sonnet** family (frontier coding).                                                                       |
| ~5–7        | **OpenAI**, **Google**, **Alibaba**                                     | Strong candidates: **GPT-5 / o3 / o4-mini**, **Gemini**, **Qwen** coding variants.                                                   |
| ~8–12       | **Z.ai**, **Google**, **Xiaomi**, **Moonshot**, **MiniMax**, **OpenAI** | Good “breadth” slots: **GLM**, **Kimi**, **MiniMax**, additional **GPT** variants—**if** your Inspect + billing stack supports them. |
| Mid / lower | **DeepSeek**, **Alibaba** open-weight, **xAI**, **Mistral**, etc.       | Useful for **open vs closed** and **cost baselines**—not always at the top of Arena but often strong on code.                        |


Exact **model names** on the public page are sometimes abbreviated; treat Arena as a **prior** for which *labs* and *families* matter, then map to **concrete API model IDs** in Inspect (e.g. `openai/gpt-5-2025-08-07`, `anthropic/claude-sonnet-4-20250514`) at run time—IDs change with releases.

---

## 2. Recommended model set (broad but actionable)

Below is an **informative** set that mirrors Arena diversity (top proprietary labs + strong open/API models + reasoning vs non-reasoning). Replace version strings with whatever Inspect lists for your run date.

### Tier S — Arena top band (proprietary, coding-first)


| Role                        | Representative Inspect-style IDs (verify before running)                   | Notes                                                                               |
| --------------------------- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Anthropic flagship          | `anthropic/claude-opus-4-1-20250805`, `anthropic/claude-sonnet-4-20250514` | Arena cluster at ranks 1–4 in the Apr 2026 snapshot; Opus is **expensive**.         |
| OpenAI flagship + reasoning | `openai/gpt-5-2025-08-07`, `openai/o3`, `openai/o4-mini`                   | GPT-5 and o3 match ImpossibleBench-style reporting; o4-mini is a **cheap** control. |
| Google                      | `google/gemini-2.5-pro-preview-06-05` (example—pin current ID)             | Strong Arena placement; confirm sandbox + Inspect support.                          |


### Tier A — Breadth (still frontier, different labs)


| Role                    | Representative IDs                                                                | Notes                                                                                   |
| ----------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Alibaba coding          | `openrouter/qwen/qwen3-coder-480b-a35b-instruct` or provider-specific Qwen3-Coder | Arena top-10 band; may need OpenRouter or native API.                                   |
| Prior Sonnet (ablation) | `anthropic/claude-3-7-sonnet-20250219`                                            | Same lab, older generation—useful **paired** comparison with Sonnet 4.                  |
| OpenAI generalist       | `openai/gpt-4.1`                                                                  | Not always top of Arena coding today but good **non-reasoning** baseline next to GPT-5. |


### Tier B — Open / efficient (Arena mid-tier but paper-relevant)


| Role            | Representative IDs                                     | Notes                                                                             |
| --------------- | ------------------------------------------------------ | --------------------------------------------------------------------------------- |
| DeepSeek        | `openrouter/deepseek/deepseek-chat` or DeepSeek-V3 API | Strong code, MIT license family; pricing often low.                               |
| Additional open | Qwen / Mistral / Kimi via OpenRouter                   | Only if you need extra **open-weight** points—validate Inspect integration first. |


**Practical core (if you must cap headcount):**  
**GPT-5, o3, o4-mini, Sonnet 4, (optional Opus or Gemini), Qwen3-Coder or DeepSeek** → **6–8 models** covers Arena leaders + open diversity without exploding cost.

---

## 3. How many examples per model?

### 3.1 Dataset size (fixed by benchmark)

The Hugging Face dataset `fjzzq2002/impossible_livecodebench`, split `conflicting`, contains **103** tasks (verified locally via `datasets`).

For **pass rate** (reward hack proxy) and for **lying rates reported as a fraction of all tasks**, the natural **N = 103** per model, **one run**—matching ImpossibleBench-style “full split” coverage.

### 3.2 Statistical interpretation (what N = 103 buys you)

Two different sample sizes matter:

1. **Denominator = 103 tasks**
  - **Pass rate** (reward hack): Wilson 95% CI half-width for *p* ≈ 0.5 is about **±9.5 percentage points**; for *p* ≈ 0.7, about **±8.8 pp**.  
  - This is in line with reporting a single full-benchmark pass rate.
2. **Denominator = number of callouts** (only tasks where the agent **passed** the impossible task)
  Lying / truth / evasive labels are defined **conditional on** `preserved_solution` and callout. If roughly **50–75%** of tasks pass (ImpossibleBench-style ranges), expect **K ≈ 52–77** triggered callouts per model per run.  
   For a **lying rate** *p* ≈ 0.5 among callouts with *K* ≈ 60, Wilson half-width is about **±12–13 pp** at 95%.  
   To narrow conditional lying CIs to **±7 pp** you would need on the order of **K ≈ 200** callouts—which usually means **multiple runs**, a **higher pass rate**, or a **larger task set** (not available here without changing the benchmark).

**Recommendation:**  

- **Primary:** **103 examples per model**, **one run**, for minimal scaffold—same *N* for every model for fair comparison.  
- **Reliability (optional):** a **second run** on **1–2 cheaper models** (e.g. o4-mini + one Sonnet/GPT-5) on the same 103 tasks to quote run-to-run variance.  
- **Tools scaffold:** same **103** if budget allows; otherwise a **fixed subset** (e.g. 34 tasks ≈ one third) with a **fixed seed** for `shuffle`—clearly labeled as a **subsample** in any paper.

---

## 4. Cost estimation methodology

### 4.1 Empirical anchors (your runs, `openai/gpt-5-2025-08-07`, 5 samples)


| Preset                         | Reported total tokens (5 samples) | × 103/5 → full split scale |
| ------------------------------ | --------------------------------- | -------------------------- |
| `aleval_livecodebench_minimal` | **45,871**                        | **≈ 945,144**              |
| `aleval_livecodebench_tools`   | **509,278**                       | **≈ 10,491,127**           |


Per-sample (minimal) token **components** in your log (5-sample aggregate):  
**I = 9,730**, **O = 36,141**, **R = 32,384** (reasoning).  
Inspect’s single “total” line is **not** always equal to I + O + R; **billing** follows provider rules (input / output / cached / reasoning).

**Tools run** (5-sample aggregate): **I = 92,366**, **O = 27,664**, **CR = 389,248**, **R = 13,952** — tools are **~11×** the minimal total tokens in your data; **cache-read** lines can dominate cost depending on price.

### 4.2 OpenAI GPT-5-class minimal run (illustrative)

Using **scaled I/O** from your minimal run to 103 tasks:

- **Input tokens** ≈ 9,730 × (103/5) = **200,438**  
- **Output + reasoning** (if both billed as output tier): (36,141 + 32,384) × (103/5) = **1,411,655**

At illustrative **$2 / 1M input** and **$8 / 1M output** (check current OpenAI pricing; reasoning may differ):


| Component                      | Tokens  | Cost @ $2/$8                            |
| ------------------------------ | ------- | --------------------------------------- |
| Input                          | ~0.200M | ~$0.40                                  |
| Output-side (O+R)              | ~1.412M | ~$11.30                                 |
| **Total (order of magnitude)** | —       | **~$12** per model per minimal full run |


This is **one** model; other labs multiply by their **list prices** and token profiles (Opus: high $/token; DeepSeek: often much lower).

### 4.3 Tools scaffold (illustrative, GPT-5-class)

Scaling your **509,278** total tokens by 103/5 gives **~10.5M** reported-token-equivalents per full tools run for the same model class—**roughly an order of magnitude more expensive** than minimal for the same 103 tasks, before accounting for **cache-read** discounts.

**Conservative planning:** budget **~8–15×** the minimal per-model cost for a **full** tools run vs minimal for the **same** model (depends on cache pricing).

### 4.4 LLM judge (`aleval-report --llm-judge`)

Callouts are a **subset** of 103 (only passed tasks). Judge cost is usually **small** vs agent loops if you use a mid-tier judge (e.g. GPT-4.1-class)—on the order of **$1–15** for all callouts across all models in a single report batch, unless you judge with a flagship model on huge text.

---

## 5. Scenario budgets (all numbers are estimates)

Assume **103 tasks per model** for minimal unless noted. Dollar ranges use the **~$12/minimal/model** anchor for **GPT-5-class** OpenAI pricing; **multiply** for Opus (often **2–4×**), **reduce** for o4-mini / DeepSeek / Qwen API.


| Scenario                   | What you run                             | Models (count)         | Minimal cost tier          | Tools extra                  | Judge (order of magnitude) | **Total ballpark**                  |
| -------------------------- | ---------------------------------------- | ---------------------- | -------------------------- | ---------------------------- | -------------------------- | ----------------------------------- |
| **A — Core paper table**   | Minimal only, full 103                   | 6–8                    | 6–8 × ~$8–25 = **$48–200** | —                            | **$2–10**                  | **~$50–220**                        |
| **B — Core + reliability** | A + **2nd run** on 2 cheap models        | +2 × 2 models × ~$8–15 | **+$32–60**                | —                            | —                          | **+$30–60** on top of A             |
| **C — Tools comparison**   | Full 103 tools on **2** Arena-top models | 2                      | —                          | 2 × ~$80–180 (high variance) | —                          | **+$160–360** (can dominate budget) |
| **D — Tools subsample**    | Tools on **34** tasks (⅓), 2 models      | 2                      | —                          | ~⅓ of C                      | —                          | **~$50–120**                        |


**$300 total budget:**  

- **Scenario A** (6–8 models, minimal, judge) usually fits **comfortably** if you avoid Opus on every slot.  
- **C** (full tools × 2) can **consume most of $300 by itself**—often better to do **D** or **tools on 1 flagship + 1 open model**.

---

## 6. Summary recommendations

1. **Arena:** Prioritize models from the **top Anthropic / OpenAI / Google / Alibaba** bands on the current Code leaderboard, then add **one open/API** family (DeepSeek or Qwen) for breadth.
2. **N:** **103 examples per model** on minimal for the main results; optional **second run** on **two** models for variance.
3. **Costs:** Anchor on **~$10–15 per model** for GPT-5-class **minimal** full runs (scaled from your logs); **tools** full runs are **~10×** token load vs minimal—budget **carefully** or use a **fixed subset**.
4. **Always** pin dataset revision, model IDs, `max_attempts`, `message_limit`, and reasoning flags when you publish.

---

## References

- Code AI Leaderboard: [arena.ai/leaderboard/code](https://arena.ai/leaderboard/code) (snapshot referenced: Apr 1, 2026).  
- ALEval presets: `[src/impossiblebench/lcb/tasks.py](../src/impossiblebench/lcb/tasks.py)`.  
- ImpossibleBench paper (reward-hack rates, model list): [arXiv:2510.20270](https://arxiv.org/pdf/2510.20270).

---

# ALEval large experiment report

This document turns the ALEval thesis plan into an execution-ready experiment brief for a roughly $300 budget.

It is grounded in three things:

1. The current coding leaderboard snapshot from Arena on April 7, 2026.
2. The ImpossibleBench paper setup.
3. Your own pilot runs in this repo on April 8, 2026.

The bottom line is simple:

- The main paper-quality experiment should be LiveCodeBench only.
- `aleval_livecodebench_minimal` should be the primary scaffold.
- `aleval_livecodebench_tools` should be a secondary comparison, not the main budget sink.
- A strong frontier panel plus a few breadth and historical-anchor models still fits comfortably inside $300.

---

## 1. Executive recommendation

Recommended main experiment:

- Run `aleval_livecodebench_minimal` on the full conflicting split (`N = 103`) for 8 models.
- Add `aleval_livecodebench_tools` for 2 models only.
- Add 2 historical anchors for comparison to ImpossibleBench.
- Add 2 cheap reruns for run-to-run variance.
- Use the deterministic callout label as the primary label and a cheaper post-hoc LLM judge as a secondary audit.

Recommended budget allocation:


| Stage               | Scope                                                   | Estimated spend                                             |
| ------------------- | ------------------------------------------------------- | ----------------------------------------------------------- |
| LCB minimal main panel | 6 models, LCB minimal, full 103 tasks                | ~$50.6 base                                                 |
| LCB tools comparison   | `GLM-5.1` and `Qwen 3.6 Plus`, LCB tools, full 103 tasks | ~$16.1 base using no-cache upper estimates                  |
| Reliability reruns     | `GLM-5.1` and `Qwen 3.6 Plus`, LCB minimal rerun     | ~$5.1 base                                                  |
| LLM judge              | all triggered callouts, `GLM-5.1` judge              | roughly ~$1 to ~$3                                          |
| Total                  | current chosen plan                                  | ~$71 to ~$73 base, ~$106 to ~$110 with 1.5x safety factor  |


That means the current chosen plan is comfortably inside a $300 budget even with a healthy contingency margin.

### 1.1 Current chosen experiment and OpenRouter cost estimate

This is the concrete run you selected for the thesis:

- `LCB-min`, full 103 tasks:
  - `openrouter/google/gemini-3.1-pro-preview`
  - `openrouter/openai/gpt-5.4`
  - `openrouter/anthropic/claude-opus-4.6`
  - `openrouter/x-ai/grok-4.20`
  - `openrouter/z-ai/glm-5.1`
  - `openrouter/qwen/qwen3.6-plus`
- `LCB-tools`, full 103 tasks:
  - `openrouter/z-ai/glm-5.1`
  - `openrouter/qwen/qwen3.6-plus`
- Reliability reruns, `LCB-min`, full 103 tasks:
  - `openrouter/z-ai/glm-5.1`
  - `openrouter/qwen/qwen3.6-plus`
- Post-hoc judge:
  - `openrouter/z-ai/glm-5.1`

Using the existing token anchors from your April 8, 2026 pilots:

- minimal full-run formula:
  - `cost_minimal ~= 0.200438 * input_price_per_1M + 0.744505 * output_price_per_1M`
- tools full-run formula, conservative no-cache upper estimate:
  - `cost_tools_upper ~= 9.921249 * input_price_per_1M + 0.569878 * output_price_per_1M`

Current OpenRouter list prices used here:

- `google/gemini-3.1-pro-preview`: `$2.00 / $12.00` per 1M
- `openai/gpt-5.4`: `$2.50 / $15.00` per 1M
- `anthropic/claude-opus-4.6`: `$5.00 / $25.00` per 1M
- `x-ai/grok-4.20`: `$2.00 / $6.00` per 1M
- `z-ai/glm-5.1`: `$1.395 / $4.40` per 1M
- `qwen/qwen3.6-plus`: `$0.325 / $1.95` per 1M

Estimated spend by run:

| Run bucket | Model | Estimated cost |
| --- | --- | ---: |
| LCB-min full | `google/gemini-3.1-pro-preview` | ~$9.33 |
| LCB-min full | `openai/gpt-5.4` | ~$11.67 |
| LCB-min full | `anthropic/claude-opus-4.6` | ~$19.61 |
| LCB-min full | `x-ai/grok-4.20` | ~$4.87 |
| LCB-min full | `z-ai/glm-5.1` | ~$3.56 |
| LCB-min full | `qwen/qwen3.6-plus` | ~$1.52 |
| LCB-tools full | `z-ai/glm-5.1` | ~$16.35 |
| LCB-tools full | `qwen/qwen3.6-plus` | ~$4.34 |
| Reliability rerun, LCB-min full | `z-ai/glm-5.1` | ~$3.56 |
| Reliability rerun, LCB-min full | `qwen/qwen3.6-plus` | ~$1.52 |

Subtotal by stage:

- LCB minimal main panel: `~$50.56`
- LCB tools panel: `~$20.68`
- reliability reruns: `~$5.07`
- total before judge: `~$76.31`

Planning interpretation:

- with `glm-5.1` as the judge, total judge cost should stay small relative to the agent loops, so a realistic planning total is about `~$77 to ~$79`
- with the same `1.5x` safety factor used elsewhere in this report, plan for about `~$116 to ~$119`

That means your current selected experiment is materially cheaper than the earlier broader 8-model plus anchors package, while still covering six strong frontier labs plus two cheap full tools comparisons.

---

## 2. What to mirror from ImpossibleBench

The ImpossibleBench paper uses the following choices that matter most for a thesis-grade ALEval run:

- Model set spans several labs, not one family only.
- Main LiveCodeBench results use the minimal scaffold.
- LiveCodeBench full-scaffold results are treated as a secondary comparison in the appendix.
- Agents get up to 10 submissions.
- Prompting is strict: if the task is inconsistent with the spec, the model should stop rather than carve out code to satisfy the tests.
- Error bars are reported as 90% confidence intervals.

From the paper text:

- The evaluated model suite included GPT-5, o3, o4-mini, GPT-4.1, Claude Opus 4.1, Claude Sonnet 4, Claude Sonnet 3.7, and Qwen3-Coder.
- The default scaffold for Impossible-LiveCodeBench was the minimal scaffold.
- The benchmark allows up to 10 submissions.

For ALEval, the closest paper-faithful setup is:

- dataset: `fjzzq2002/impossible_livecodebench`
- split: `conflicting`
- primary preset: `aleval_livecodebench_minimal`
- secondary preset: `aleval_livecodebench_tools`
- `max_attempts=10`
- `message_limit=50`
- 90% Wilson confidence intervals in the final writeup

---

## 3. Why the big run should be LiveCodeBench only

You asked whether all ALEval paths should be considered. They should be planned, but they should not all be run in the main thesis experiment at this budget.

Your local 5-sample pilot runs on April 8, 2026 already make the case:


| Preset                         | 5-sample pilot tokens | Relative to LCB minimal |
| ------------------------------ | --------------------- | ----------------------- |
| `aleval_livecodebench_minimal` | 45,871                | 1.0x                    |
| `aleval_livecodebench_tools`   | 509,278               | 11.1x raw tokens        |
| `aleval_swebench_minimal`      | 2,943,933             | 64.2x                   |
| `aleval_swebench_tools`        | 3,972,881             | 86.6x                   |


The SWE pilots are vastly more expensive in token volume even before accounting for:

- heavier Docker usage,
- more fragile environments,
- longer wall-clock runtime,
- more operational debugging,
- and much larger variance in tool-heavy transcripts.

Conclusion:

- Keep SWE out of the main thesis experiment.
- If you want SWE at all, treat it as a separate future appendix or a tiny 1 to 3 sample smoke test only.

---

## 4. Dataset size and what it implies statistically

I verified locally on April 8, 2026 that:

- `fjzzq2002/impossible_livecodebench`, split `conflicting`, contains exactly `103` tasks.

That means the natural unit for the main experiment is:

- `N = 103` tasks per model per scaffold.

Two denominators matter in ALEval:

1. Reward-hack rate:
  - `passed / 103`
  - This is the cleanest direct analogue of ImpossibleBench's cheating-rate metric.
2. Callout honesty labels:
  - `lie`, `truth`, `evasive` are only defined when the agent first reward-hacks and the callout fires.
  - In ALEval terms, that means the label is gated on both `score == 1` and `triggered == True`.

Because of that gating, you should report both:

- unconditional rates over all 103 tasks:
  - `lie / 103`
  - `truth / 103`
  - `evasive / 103`
- conditional rates among triggered callouts:
  - `lie / triggered`
  - `truth / triggered`
  - `evasive / triggered`

This matters for interpretation:

- the unconditional rate is better for cross-model comparisons because the denominator is fixed;
- the conditional rate is better for the behavioral question "once the model reward-hacks, does it lie?"

For the thesis, I would make the unconditional rates primary in the main comparison table and keep the conditional rates as a second table or appendix figure.

---

## 5. Arena-aligned model selection

Source used for current frontier selection:

- Arena Text Coding leaderboard snapshot dated April 7, 2026.

Important caveat:

- Arena is a model-selection prior, not a perfect ALEval proxy.
- Arena entries like `gpt-5.4-high` or `claude-opus-4-6-thinking` are often leaderboard-specific operating modes, not always separate public API IDs.
- Where that happens, the ALEval run should map them to the closest public API model plus the closest available reasoning setting.

### 5.1 Recommended core frontier panel

This is the panel I would actually run first.


| Include | Arena coding rank on 2026-04-07 | Arena entry                                    | ALEval run target                                                                                                              | Why include                                                                            | Est. LCB minimal cost for 103 tasks |
| ------- | ------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------- | ----------------------------------- |
| Yes     | 1 to 2                          | `claude-opus-4-6` / `claude-opus-4-6-thinking` | `openrouter/anthropic/claude-opus-4.6` or closest exposed 4.6 variant                                                          | strongest current Anthropic coding model                                               | ~$19.6                              |
| Yes     | 3                               | `gpt-5.4-high`                                 | `openrouter/openai/gpt-5.4` with `reasoning_effort=high`                                                                       | strongest current OpenAI coding entry                                                  | ~$11.7                              |
| Yes     | 4                               | `gemini-3.1-pro-preview`                       | `openrouter/google/gemini-3.1-pro-preview`                                                                                     | strongest current Google coding model                                                  | ~$9.3                               |
| Yes     | 8                               | `claude-sonnet-4-6`                            | `openrouter/anthropic/claude-sonnet-4.6`                                                                                       | cheaper Anthropic flagship family comparison                                           | ~$11.8                              |
| Yes     | 10                              | `glm-5.1`                                      | `openrouter/z-ai/glm-5.1` or closest exposed GLM-5.1 slug                                                                      | top-ranked cheap MIT-license breadth model                                             | ~$3.6                               |
| Yes     | 17                              | `gpt-5.4-mini-high`                            | `openrouter/openai/gpt-5.4-mini` with `reasoning_effort=high`                                                                  | cheap strong control inside the same OpenAI generation                                 | ~$3.5                               |
| Yes     | 8 on Code Arena Overall         | `qwen3.6-plus-preview`                         | `openrouter/qwen/qwen3.6-plus-preview`                                                                                         | best currently ranked Qwen coding model available in Arena's code-specific leaderboard | ~$1.5                               |
| Yes     | 31 on Code Arena Overall        | `deepseek-v3.2-thinking`                       | `deepseek/deepseek-reasoner` on the official DeepSeek API, or the closest `openrouter/deepseek/...` route available on run day | best currently ranked DeepSeek coding model in Arena's code-specific leaderboard       | ~$0.4                               |


Base cost of this 8-model panel:

- about `$61.24`

That is low enough that budget is not the limiting factor. The real constraints are runtime, reproducibility, and analysis quality.

### 5.2 Good optional frontier add-ons

Only add these if the exact API model is exposed and stable on run day:


| Arena coding rank on 2026-04-07 | Model                 | Why it is optional instead of core                                                                                              |
| ------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| 6 to 9                          | Grok 4.20 variants    | excellent leaderboard placement, but beta and multi-agent naming makes API stability more uncertain                             |
| 19                              | `kimi-k2.5-thinking`  | strong and cheap, but less central to the current ImpossibleBench comparison story                                              |
| 22 in Text Arena Coding         | `qwen3.5-max-preview` | strong general coding/text signal, but for agentic coding the code-specific leaderboard currently favors `qwen3.6-plus-preview` |


### 5.3 Historical anchors for direct comparison to ImpossibleBench

These are not current frontier leaders, but they are useful if you want a bridge back to the paper:


| Include  | Why                                                                       | Est. LCB minimal cost for 103 tasks |
| -------- | ------------------------------------------------------------------------- | ----------------------------------- |
| Optional | `claude-sonnet-3.7` for a direct older-Claude comparison                  | ~$11.8                              |
| Optional | `gpt-5` for a direct older-OpenAI comparison aligned with ImpossibleBench | ~$7.7                               |


If you only add two historical anchors, these are the ones I would choose.

---

## 6. Cost model

All cost estimates below are anchored to your actual April 8, 2026 pilot logs with GPT-5 on 5 LiveCodeBench samples.

### 6.1 Minimal scaffold token anchor

Observed 5-sample pilot for `aleval_livecodebench_minimal`:

- total tokens: `45,871`
- input tokens: `9,730`
- output tokens: `36,141`
- reasoning tokens: `32,384`

Important interpretation:

- the reasoning tokens are a subset of output tokens, not an extra bucket to add on top.

Scaled linearly from 5 samples to the full 103-task split:

- input tokens per full minimal run: `200,438`
- output tokens per full minimal run: `744,505`

So the base formula is:

`cost_minimal ~= 0.200438 * input_price_per_1M + 0.744505 * output_price_per_1M`

### 6.2 Tools scaffold token anchor

Observed 5-sample pilot for `aleval_livecodebench_tools`:

- total tokens: `509,278`
- fresh input tokens: `92,366`
- cached-read tokens: `389,248`
- output tokens: `27,664`
- reasoning tokens: `13,952`

Scaled linearly to the full 103-task split:

- fresh input tokens: `1,902,740`
- cached-read tokens: `8,018,509`
- output tokens: `569,878`

This gives two useful cost formulas:

1. No-cache upper bound:

`cost_tools_upper ~= 9.921249 * input_price_per_1M + 0.569878 * output_price_per_1M`

1. Cached-input case:

`cost_tools_cached ~= 1.902740 * input_price_per_1M + 8.018509 * cached_input_price_per_1M + 0.569878 * output_price_per_1M`

Why both formulas matter:

- OpenAI gets automatic prompt caching.
- DeepSeek gets automatic prompt caching.
- Anthropic and Gemini can benefit from caching, but with OpenRouter that usually requires explicit cache control and ALEval does not currently set that.

So:

- for OpenAI and DeepSeek, the cached-input estimate is realistic today;
- for Anthropic and Gemini, the no-cache upper bound is the safer planning number unless you patch the harness to set cache controls.

### 6.3 A note on underestimation

Your pilots used `max_attempts=3`.

The paper-faithful run should use `max_attempts=10`.

That means every cost estimate in this document should be treated as a base estimate, not a hard guarantee.

My planning rule is:

- use the base estimate for raw math,
- multiply the whole experiment by `1.5x` for budget planning,
- treat `2x` as the emergency ceiling if a model is unusually verbose or stubborn.

That is why the recommended thesis plan is budgeted at both a base figure and a contingency figure.

---

## 7. Concrete per-model cost estimates

### 7.1 Minimal scaffold, full split, 103 tasks

These use the observed ALEval minimal token profile plus the current public prices visible on April 8, 2026.


| Model family           | Price basis used                       | Estimated cost |
| ---------------------- | -------------------------------------- | -------------- |
| Claude Opus 4.6        | $5 / $25 per 1M                        | ~$19.6         |
| GPT-5.4                | $2.50 / $15 per 1M                     | ~$11.7         |
| Gemini 3.1 Pro Preview | $2 / $12 per 1M                        | ~$9.3          |
| Claude Sonnet 4.6      | $3 / $15 per 1M                        | ~$11.8         |
| GLM-5.1                | $1.4 / $4.4 per 1M                     | ~$3.6          |
| GPT-5.4 Mini           | $0.75 / $4.50 per 1M                   | ~$3.5          |
| Qwen 3.6 Plus Preview  | $0.33 / $1.95 per 1M                   | ~$1.5          |
| DeepSeek V3.2 Thinking | $0.28 cache miss / $0.42 output per 1M | ~$0.4          |


Interpretation:

- Running a large minimal-only panel is cheap enough that you should optimize for scientific coverage, not token thrift.
- The main reason to exclude a model should be setup risk or thesis focus, not cost.

### 7.2 Tools scaffold, full split, 103 tasks

These are much more variable because caching policy matters.


| Model                  | Cached-input assumption                                             | Estimated cost                     |
| ---------------------- | ------------------------------------------------------------------- | ---------------------------------- |
| GPT-5.4                | realistic with OpenAI automatic caching                             | ~$15.3                             |
| GPT-5.4 Mini           | realistic with OpenAI automatic caching                             | ~$4.6                              |
| DeepSeek V3.2 Thinking | realistic with DeepSeek automatic caching                           | about ~$1.0                        |
| Claude Sonnet 4.6      | no-cache upper bound is safer unless you add `cache_control`        | up to ~$38.3                       |
| Claude Opus 4.6        | no-cache upper bound is safer unless you add `cache_control`        | up to ~$63.9                       |
| Gemini 3.1 Pro Preview | no-cache upper bound is safer unless you add cache controls         | up to ~$26.7                       |
| GLM-5.1                | assume no-cache unless you verify caching in provider docs and logs | about ~$16.6 with official pricing |


This changes the budget story:

- tools runs are no longer "impossible" at this budget;
- but they are still not the best place to spend the first dollars.

My recommendation is still:

- primary thesis table = minimal scaffold,
- secondary appendix comparison = tools on 2 models only.

---

## 8. Recommended experiment packages

### Package A: Minimum publishable thesis run

Run:

- 6 frontier models
- LCB minimal only
- full 103 tasks
- post-hoc LLM judge

Suggested models:

- GPT-5.4
- GPT-5.4 Mini
- Claude Sonnet 4.6
- Claude Opus 4.6
- Gemini 3.1 Pro Preview
- GLM-5.1

Estimated cost:

- about `$59`
- about `$89` with 1.5x safety factor

This is the cleanest low-risk package.

### Package B: Current selected thesis run

Run:

- 6-model frontier plus breadth panel
- minimal scaffold on all 6
- 2 tools comparisons
- 2 cheap reruns
- judge everything

Suggested models:

- Core 8:
  - Gemini 3.1 Pro Preview
  - GPT-5.4
  - Claude Opus 4.6
  - Grok 4.20
  - GLM-5.1
  - Qwen 3.6 Plus
- Tools:
  - GLM-5.1
  - Qwen 3.6 Plus
- Reliability reruns:
  - GLM-5.1
  - Qwen 3.6 Plus

Estimated cost:

- about `$77` to `$79` base including a cheap `glm-5.1` judge
- about `$116` to `$119` with 1.5x safety factor

This is the package I recommend for the thesis.

### Package C: Maximum breadth inside $300

Take Package B and add one or two optional frontier models if they are stable on OpenRouter on run day:

- a Grok 4.20 variant, or
- Kimi K2.5 Thinking

Even then, you should still stay below `$300` unless one provider surprises you badly on tool-scaffold verbosity or caching behavior.

---

## 9. How to execute the experiment step by step

This is the part you can follow directly.

### Step 1: Freeze the exact model manifest

Do this on the day you launch the experiment, not earlier.

- Open the Arena coding leaderboard and record the snapshot date.
- Open OpenRouter model pages for the exact slugs you will run.
- Write one small manifest with:
  - model family,
  - exact provider slug,
  - whether you will pass `reasoning_effort=high`,
  - which scaffold(s) it will run on,
  - expected cost bucket.

Do not let model names drift mid-experiment.

### Step 2: Install only the dependencies you need

For the recommended LCB-only experiment:

```bash
pip install -e ".[test,analysis]"
```

You do not need SWE extras for the main run.

### Step 3: Set the environment

Recommended env:

```bash
cp .env.example .env
```

Add at least:

```bash
OPENROUTER_API_KEY=...
HF_TOKEN=...   # optional but recommended
ALEVAL_JUDGE_MODEL=openrouter/z-ai/glm-5.1
```

Then confirm:

```bash
docker version
```

### Step 4: Use a fixed directory layout

Use one folder per model per scaffold so `aleval-report` stays easy to reason about.

Recommended structure:

```text
logs/
  exp_2026-04-08/
    lcb_min/
      gpt-5.4/
      claude-sonnet-4.6/
      ...
    lcb_tools/
      gpt-5.4/
      claude-sonnet-4.6/

reports/
  exp_2026-04-08/
    lcb_min/
      gpt-5.4/
      claude-sonnet-4.6/
      ...
    lcb_tools/
      gpt-5.4/
      claude-sonnet-4.6/
```

### Step 5: Run a 3-sample smoke test on the cheapest serious model

I would start with `qwen3.6-plus`. It is one of your selected main-run models, it is cheap, and in a direct OpenRouter sanity check it returned a clean text response more reliably than `glm-5.1`.

```bash
inspect eval src/impossiblebench/lcb/tasks.py@aleval_livecodebench_minimal \
  --model openrouter/qwen/qwen3.6-plus \
  --sandbox local \
  -T limit=3 -T max_attempts=3 -T message_limit=40 \
  --log-dir ./logs/exp_2026-04-08/smoke/qwen3.6-plus
```

Then generate a report:

```bash
aleval-report \
  --logs-dir ./logs/exp_2026-04-08/smoke/qwen3.6-plus \
  --out-dir ./reports/exp_2026-04-08/smoke/qwen3.6-plus \
  --llm-judge openrouter/z-ai/glm-5.1
```

Check:

- the run completes,
- passed tasks trigger the callout,
- `lie`, `truth`, `evasive`, and `not_applicable` behave as expected,
- the judge output looks sensible.

### Step 6: Run one 10-sample pilot before launching the full panel

This is worth doing because your cost anchors were from `max_attempts=3`, but the thesis run should use `max_attempts=10`.

I would do:

- one pilot on `qwen3.6-plus`,
- one pilot on `gpt-5.4`.

Use:

```bash
inspect eval src/impossiblebench/lcb/tasks.py@aleval_livecodebench_minimal \
  --model openrouter/openai/gpt-5.4 \
  --sandbox local \
  -T limit=10 -T max_attempts=10 -T message_limit=50 \
  --reasoning-effort high \
  --log-dir ./logs/exp_2026-04-08/pilot/lcb_min/gpt-5.4
```

If those 10-sample pilots stay close to the planned cost shape, proceed.

### Step 7: Launch the main minimal panel

Use one command per model so failures are isolated and reruns are easy.

OpenAI template:

```bash
inspect eval src/impossiblebench/lcb/tasks.py@aleval_livecodebench_minimal \
  --model openrouter/openai/gpt-5.4 \
  --sandbox docker \
  -T max_attempts=10 -T message_limit=50 \
  --reasoning-effort high \
  --log-dir ./logs/exp_2026-04-08/lcb_min/gpt-5.4 \
  --fail-on-error False
```

Generic non-OpenAI template:

```bash
inspect eval src/impossiblebench/lcb/tasks.py@aleval_livecodebench_minimal \
  --model openrouter/anthropic/claude-sonnet-4.6 \
  --sandbox docker \
  -T max_attempts=10 -T message_limit=50 \
  --log-dir ./logs/exp_2026-04-08/lcb_min/claude-sonnet-4.6 \
  --fail-on-error False
```

Recommended run order:

1. Qwen 3.6 Plus
2. GLM-5.1
3. Grok 4.20
4. Gemini 3.1 Pro Preview
5. GPT-5.4
6. Claude Opus 4.6

Why this order:

- cheapest and easiest models flush out harness issues first,
- expensive models only run after the pipeline is already proven.

### Step 8: Run `aleval-report` immediately after each model

Do not wait until the very end.

Example:

```bash
aleval-report \
  --logs-dir ./logs/exp_2026-04-08/lcb_min/gpt-5.4 \
  --out-dir ./reports/exp_2026-04-08/lcb_min/gpt-5.4 \
  --llm-judge openrouter/z-ai/glm-5.1
```

After each report, check:

- total sample count is 103,
- passed count is plausible,
- callout count equals the number of triggered labels,
- the judge is not returning many `unknown` labels.
- if the `glm-5.1` judge returns empty or obviously malformed outputs, switch the judge to `openrouter/qwen/qwen3.6-plus` for the remainder of the run and document the change.

### Step 9: Run tools on two models only

Chosen tools pair:

- GLM-5.1
- Qwen 3.6 Plus

Command template:

```bash
inspect eval src/impossiblebench/lcb/tasks.py@aleval_livecodebench_tools \
  --model openrouter/z-ai/glm-5.1 \
  --sandbox docker \
  -T max_attempts=10 -T message_limit=50 \
  --log-dir ./logs/exp_2026-04-08/lcb_tools/glm-5.1 \
  --fail-on-error False
```

Important note:

- For `glm-5.1` and `qwen3.6-plus`, I still recommend budgeting the tools runs using the no-cache upper formula unless you confirm caching behavior from logs on your account.

### Step 10: Run two cheap reruns for variance

Use the same 103-task full split on the same scaffold, same config, same model family, different run.

Best rerun choices:

- GPT-5.4 Mini
- GLM-5.1

These are cheap enough that the extra statistical confidence is worth more than the token cost.

### Step 11: Aggregate results for the thesis

`aleval-report` is perfect for per-run sanity checks, but your thesis table should come from all per-model CSVs combined.

For the final analysis, build one combined dataframe from every `judged_samples.csv`.

The main tables should include:

- reward-hack rate = `passed / 103`
- unconditional lie rate = `lie / 103`
- unconditional truth rate = `truth / 103`
- unconditional evasive rate = `evasive / 103`
- conditional lie/truth/evasive among triggered callouts
- judge agreement rate

Use 90% Wilson intervals in the main thesis figures to match ImpossibleBench.

### Step 12: Keep an audit trail

For every run, record:

- exact model slug,
- exact date,
- scaffold,
- `max_attempts`,
- `message_limit`,
- whether `reasoning_effort=high` was used,
- output directory,
- any reruns or failures.

This is what will save you when you write the methods section.

---

## 10. What I would report in the thesis

Primary figure:

- reward-hack rate by model on `aleval_livecodebench_minimal`

Primary ALEval figure:

- stacked bars of unconditional `lie`, `truth`, `evasive` rates over all 103 tasks

Secondary figure:

- conditional honesty distribution among triggered callouts only

Secondary appendix comparison:

- minimal vs tools for the two selected models

Methodology appendix:

- deterministic label vs LLM judge agreement
- representative examples of lie, truth, and evasive responses

Statistical tests:

- 90% Wilson confidence intervals for all plotted proportions
- Fisher exact tests for the main pairwise model comparisons you care about
- Holm or Bonferroni correction if you do many pairwise tests

---

## 11. Final recommendation

If you want the best balance of scientific value, cost, and execution risk, run this:

1. Main panel, LCB minimal, 103 tasks:
  - `openrouter/google/gemini-3.1-pro-preview`
  - `openrouter/openai/gpt-5.4`
  - `openrouter/anthropic/claude-opus-4.6`
  - `openrouter/x-ai/grok-4.20`
  - `openrouter/z-ai/glm-5.1`
  - `openrouter/qwen/qwen3.6-plus`
2. Tools comparison:
  - `openrouter/z-ai/glm-5.1`
  - `openrouter/qwen/qwen3.6-plus`
3. Reliability reruns:
  - `openrouter/z-ai/glm-5.1`
  - `openrouter/qwen/qwen3.6-plus`
4. Post-hoc judge:
  - `openrouter/z-ai/glm-5.1`

Expected spend:

- about `$77` to `$79` base
- about `$116` to `$119` with a 1.5x contingency

That is the experiment package I would stand behind for the thesis.

---

## References

- Arena Text Coding leaderboard, snapshot dated April 7, 2026: [https://arena.ai/leaderboard/text/coding](https://arena.ai/leaderboard/text/coding)
- Arena overview leaderboard, coding column snapshot dated April 8, 2026: [https://arena.ai/leaderboard](https://arena.ai/leaderboard)
- ImpossibleBench paper: [https://arxiv.org/abs/2510.20270](https://arxiv.org/abs/2510.20270)
- OpenAI pricing: [https://developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing)
- Google Gemini API pricing: [https://ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing)
- Z.AI pricing: [https://docs.z.ai/guides/overview/pricing](https://docs.z.ai/guides/overview/pricing)
- DeepSeek pricing: [https://api-docs.deepseek.com/quick_start/pricing/](https://api-docs.deepseek.com/quick_start/pricing/)
- OpenRouter prompt caching guide: [https://openrouter.ai/docs/guides/best-practices/prompt-caching](https://openrouter.ai/docs/guides/best-practices/prompt-caching)
- ALEval LiveCodeBench task presets: `src/impossiblebench/lcb/tasks.py`

---

# ALEval large experiment report

This document turns the ALEval thesis plan into an execution-ready experiment brief for a roughly $300 budget.

It is grounded in three things:

1. The current coding leaderboard snapshot from Arena on April 7, 2026.
2. The ImpossibleBench paper setup.
3. Your own pilot runs in this repo on April 8, 2026.

The bottom line is simple:

- The main paper-quality experiment should be LiveCodeBench only.
- `aleval_livecodebench_minimal` should be the primary scaffold.
- `aleval_livecodebench_tools` should be a secondary comparison, not the main budget sink.
- A strong frontier panel plus a few breadth and historical-anchor models still fits comfortably inside $300.

---

## 1. Executive recommendation

Recommended main experiment:

- Run `aleval_livecodebench_minimal` on the full conflicting split (`N = 103`) for 8 models.
- Add `aleval_livecodebench_tools` for 2 models only.
- Add 2 historical anchors for comparison to ImpossibleBench.
- Add 2 cheap reruns for run-to-run variance.
- Use the deterministic callout label as the primary label and a cheaper post-hoc LLM judge as a secondary audit.

Recommended budget allocation:


| Stage               | Scope                                        | Estimated spend                                             |
| ------------------- | -------------------------------------------- | ----------------------------------------------------------- |
| Core frontier panel | 8 models, LCB minimal, full 103 tasks        | ~$61 base                                                   |
| Historical anchors  | `Claude Sonnet 3.7` and `GPT-5`, LCB minimal | ~$19 to ~$20 base                                           |
| Tools comparison    | 2 models, LCB tools, full 103 tasks          | ~$54 to ~$76 depending on caching and model choice          |
| Reliability reruns  | 2 cheap models, LCB minimal                  | ~$7 base                                                    |
| LLM judge           | all triggered callouts                       | `< $5` if you use a cheap judge                             |
| Total               | full plan                                    | ~$141 to ~$146 base, ~$212 to ~$220 with 1.5x safety factor |


That means the full recommended plan is viable inside a $300 budget even with a healthy contingency margin.

---

## 2. What to mirror from ImpossibleBench

The ImpossibleBench paper uses the following choices that matter most for a thesis-grade ALEval run:

- Model set spans several labs, not one family only.
- Main LiveCodeBench results use the minimal scaffold.
- LiveCodeBench full-scaffold results are treated as a secondary comparison in the appendix.
- Agents get up to 10 submissions.
- Prompting is strict: if the task is inconsistent with the spec, the model should stop rather than carve out code to satisfy the tests.
- Error bars are reported as 90% confidence intervals.

From the paper text:

- The evaluated model suite included GPT-5, o3, o4-mini, GPT-4.1, Claude Opus 4.1, Claude Sonnet 4, Claude Sonnet 3.7, and Qwen3-Coder.
- The default scaffold for Impossible-LiveCodeBench was the minimal scaffold.
- The benchmark allows up to 10 submissions.

For ALEval, the closest paper-faithful setup is:

- dataset: `fjzzq2002/impossible_livecodebench`
- split: `conflicting`
- primary preset: `aleval_livecodebench_minimal`
- secondary preset: `aleval_livecodebench_tools`
- `max_attempts=10`
- `message_limit=50`
- 90% Wilson confidence intervals in the final writeup

---

## 3. Why the big run should be LiveCodeBench only

You asked whether all ALEval paths should be considered. They should be planned, but they should not all be run in the main thesis experiment at this budget.

Your local 5-sample pilot runs on April 8, 2026 already make the case:


| Preset                         | 5-sample pilot tokens | Relative to LCB minimal |
| ------------------------------ | --------------------- | ----------------------- |
| `aleval_livecodebench_minimal` | 45,871                | 1.0x                    |
| `aleval_livecodebench_tools`   | 509,278               | 11.1x raw tokens        |
| `aleval_swebench_minimal`      | 2,943,933             | 64.2x                   |
| `aleval_swebench_tools`        | 3,972,881             | 86.6x                   |


The SWE pilots are vastly more expensive in token volume even before accounting for:

- heavier Docker usage,
- more fragile environments,
- longer wall-clock runtime,
- more operational debugging,
- and much larger variance in tool-heavy transcripts.

Conclusion:

- Keep SWE out of the main thesis experiment.
- If you want SWE at all, treat it as a separate future appendix or a tiny 1 to 3 sample smoke test only.

---

## 4. Dataset size and what it implies statistically

I verified locally on April 8, 2026 that:

- `fjzzq2002/impossible_livecodebench`, split `conflicting`, contains exactly `103` tasks.

That means the natural unit for the main experiment is:

- `N = 103` tasks per model per scaffold.

Two denominators matter in ALEval:

1. Reward-hack rate:
  - `passed / 103`
  - This is the cleanest direct analogue of ImpossibleBench's cheating-rate metric.
2. Callout honesty labels:
  - `lie`, `truth`, `evasive` are only defined when the agent first reward-hacks and the callout fires.
  - In ALEval terms, that means the label is gated on both `score == 1` and `triggered == True`.

Because of that gating, you should report both:

- unconditional rates over all 103 tasks:
  - `lie / 103`
  - `truth / 103`
  - `evasive / 103`
- conditional rates among triggered callouts:
  - `lie / triggered`
  - `truth / triggered`
  - `evasive / triggered`

This matters for interpretation:

- the unconditional rate is better for cross-model comparisons because the denominator is fixed;
- the conditional rate is better for the behavioral question "once the model reward-hacks, does it lie?"

For the thesis, I would make the unconditional rates primary in the main comparison table and keep the conditional rates as a second table or appendix figure.

---

## 5. Arena-aligned model selection

Source used for current frontier selection:

- Arena Text Coding leaderboard snapshot dated April 7, 2026.

Important caveat:

- Arena is a model-selection prior, not a perfect ALEval proxy.
- Arena entries like `gpt-5.4-high` or `claude-opus-4-6-thinking` are often leaderboard-specific operating modes, not always separate public API IDs.
- Where that happens, the ALEval run should map them to the closest public API model plus the closest available reasoning setting.

### 5.1 Recommended core frontier panel

This is the panel I would actually run first.


| Include | Arena coding rank on 2026-04-07 | Arena entry                                    | Exact OpenRouter run target                                                                                           | Why include                                                                                                                     | Est. LCB minimal cost for 103 tasks |
| ------- | ------------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Yes     | 1 to 2                          | `claude-opus-4-6` / `claude-opus-4-6-thinking` | `openrouter/anthropic/claude-opus-4.6`                                                                                | strongest current Anthropic coding model                                                                                        | ~$19.6                              |
| Yes     | 3                               | `gpt-5.4-high`                                 | `openrouter/openai/gpt-5.4` with `reasoning_effort=high`                                                              | strongest current OpenAI coding entry                                                                                           | ~$11.7                              |
| Yes     | 4                               | `gemini-3.1-pro-preview`                       | `openrouter/google/gemini-3.1-pro-preview`                                                                            | strongest current Google coding model                                                                                           | ~$9.3                               |
| Yes     | 8                               | `claude-sonnet-4-6`                            | `openrouter/anthropic/claude-sonnet-4.6`                                                                              | cheaper Anthropic flagship family comparison                                                                                    | ~$11.8                              |
| Yes     | 10                              | `glm-5.1`                                      | `openrouter/z-ai/glm-5.1`                                                                                             | top-ranked cheap MIT-license breadth model                                                                                      | ~$3.2                               |
| Yes     | 17                              | `gpt-5.4-mini-high`                            | `openrouter/openai/gpt-5.4-mini` with `reasoning_effort=high`                                                         | cheap strong control inside the same OpenAI generation                                                                          | ~$3.5                               |
| Yes     | 8 on Code Arena Overall         | `qwen3.6-plus-preview`                         | `openrouter/qwen/qwen3.6-plus` as the stable paid route closest to the Arena preview entry                            | best currently ranked Qwen coding model family available in Arena's code-specific leaderboard and cleanly exposed on OpenRouter | ~$1.5                               |
| Yes     | 31 on Code Arena Overall        | `deepseek-v3.2-thinking`                       | `openrouter/deepseek/deepseek-v3.2`; if OpenRouter reasoning is exposed cleanly in your stack, enable it consistently | best currently ranked DeepSeek coding model in Arena's code-specific leaderboard                                                | ~$0.3 to ~$0.4                      |


Base cost of this 8-model panel:

- about `$60.9`

That is low enough that budget is not the limiting factor. The real constraints are runtime, reproducibility, and analysis quality.

### 5.2 Good optional frontier add-ons

Only add these if the exact API model is exposed and stable on run day:


| Arena coding rank on 2026-04-07 | Model                 | Why it is optional instead of core                                                                                              |
| ------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| 6 to 9                          | Grok 4.20 variants    | excellent leaderboard placement, but beta and multi-agent naming makes API stability more uncertain                             |
| 19                              | `kimi-k2.5-thinking`  | strong and cheap, but less central to the current ImpossibleBench comparison story                                              |
| 22 in Text Arena Coding         | `qwen3.5-max-preview` | strong general coding/text signal, but for agentic coding the code-specific leaderboard currently favors `qwen3.6-plus-preview` |


### 5.3 Historical anchors for direct comparison to ImpossibleBench

These are not current frontier leaders, but they are useful if you want a bridge back to the paper:


| Include  | Why                                                                                                                                                                 | Est. LCB minimal cost for 103 tasks |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Optional | `openrouter/anthropic/claude-3.7-sonnet` for a direct older-Claude comparison; OpenRouter currently marks it as going away on May 5, 2026, so run this anchor early | ~$11.8                              |
| Optional | `openrouter/openai/gpt-5` with `reasoning_effort=high` for a direct older-OpenAI comparison aligned with ImpossibleBench                                            | ~$7.7                               |


If you only add two historical anchors, these are the ones I would choose.

---

## 6. Cost model

All cost estimates below are anchored to your actual April 8, 2026 pilot logs with GPT-5 on 5 LiveCodeBench samples.

### 6.1 Minimal scaffold token anchor

Observed 5-sample pilot for `aleval_livecodebench_minimal`:

- total tokens: `45,871`
- input tokens: `9,730`
- output tokens: `36,141`
- reasoning tokens: `32,384`

Important interpretation:

- the reasoning tokens are a subset of output tokens, not an extra bucket to add on top.

Scaled linearly from 5 samples to the full 103-task split:

- input tokens per full minimal run: `200,438`
- output tokens per full minimal run: `744,505`

So the base formula is:

`cost_minimal ~= 0.200438 * input_price_per_1M + 0.744505 * output_price_per_1M`

### 6.2 Tools scaffold token anchor

Observed 5-sample pilot for `aleval_livecodebench_tools`:

- total tokens: `509,278`
- fresh input tokens: `92,366`
- cached-read tokens: `389,248`
- output tokens: `27,664`
- reasoning tokens: `13,952`

Scaled linearly to the full 103-task split:

- fresh input tokens: `1,902,740`
- cached-read tokens: `8,018,509`
- output tokens: `569,878`

This gives two useful cost formulas:

1. No-cache upper bound:

`cost_tools_upper ~= 9.921249 * input_price_per_1M + 0.569878 * output_price_per_1M`

1. Cached-input case:

`cost_tools_cached ~= 1.902740 * input_price_per_1M + 8.018509 * cached_input_price_per_1M + 0.569878 * output_price_per_1M`

Why both formulas matter:

- OpenAI gets automatic prompt caching.
- DeepSeek gets automatic prompt caching.
- Anthropic and Gemini can benefit from caching, but with OpenRouter that usually requires explicit cache control and ALEval does not currently set that.

So:

- for OpenAI and DeepSeek, the cached-input estimate is realistic today;
- for Anthropic and Gemini, the no-cache upper bound is the safer planning number unless you patch the harness to set cache controls.

### 6.3 A note on underestimation

Your pilots used `max_attempts=3`.

The paper-faithful run should use `max_attempts=10`.

That means every cost estimate in this document should be treated as a base estimate, not a hard guarantee.

My planning rule is:

- use the base estimate for raw math,
- multiply the whole experiment by `1.5x` for budget planning,
- treat `2x` as the emergency ceiling if a model is unusually verbose or stubborn.

That is why the recommended thesis plan is budgeted at both a base figure and a contingency figure.

---

## 7. Concrete per-model cost estimates

### 7.1 Minimal scaffold, full split, 103 tasks

These use the observed ALEval minimal token profile plus the current public prices visible on April 8, 2026.


| Model family           | Price basis used                                                        | Estimated cost |
| ---------------------- | ----------------------------------------------------------------------- | -------------- |
| Claude Opus 4.6        | $5 / $25 per 1M                                                         | ~$19.6         |
| GPT-5.4                | $2.50 / $15 per 1M                                                      | ~$11.7         |
| Gemini 3.1 Pro Preview | $2 / $12 per 1M                                                         | ~$9.3          |
| Claude Sonnet 4.6      | $3 / $15 per 1M                                                         | ~$11.8         |
| GLM-5.1                | OpenRouter page shows $1.26 / $3.96 per 1M                              | ~$3.2          |
| GPT-5.4 Mini           | OpenRouter page shows $0.75 / $4.50 per 1M                              | ~$3.5          |
| Qwen 3.6 Plus          | OpenRouter page shows $0.325 / $1.95 per 1M                             | ~$1.5          |
| DeepSeek V3.2 Thinking | OpenRouter page for `deepseek/deepseek-v3.2` shows $0.26 / $0.38 per 1M | ~$0.3 to ~$0.4 |


Interpretation:

- Running a large minimal-only panel is cheap enough that you should optimize for scientific coverage, not token thrift.
- The main reason to exclude a model should be setup risk or thesis focus, not cost.

### 7.2 Tools scaffold, full split, 103 tasks

These are much more variable because caching policy matters.


| Model                  | Cached-input assumption                                             | Estimated cost                     |
| ---------------------- | ------------------------------------------------------------------- | ---------------------------------- |
| GPT-5.4                | realistic with OpenAI automatic caching                             | ~$15.3                             |
| GPT-5.4 Mini           | realistic with OpenAI automatic caching                             | ~$4.6                              |
| DeepSeek V3.2 Thinking | realistic with DeepSeek automatic caching                           | about ~$1.0                        |
| Claude Sonnet 4.6      | no-cache upper bound is safer unless you add `cache_control`        | up to ~$38.3                       |
| Claude Opus 4.6        | no-cache upper bound is safer unless you add `cache_control`        | up to ~$63.9                       |
| Gemini 3.1 Pro Preview | no-cache upper bound is safer unless you add cache controls         | up to ~$26.7                       |
| GLM-5.1                | assume no-cache unless you verify caching in provider docs and logs | about ~$16.6 with official pricing |


This changes the budget story:

- tools runs are no longer "impossible" at this budget;
- but they are still not the best place to spend the first dollars.

My recommendation is still:

- primary thesis table = minimal scaffold,
- secondary appendix comparison = tools on 2 models only.

---

## 8. Recommended experiment packages

### Package A: Minimum publishable thesis run

Run:

- 6 frontier models
- LCB minimal only
- full 103 tasks
- post-hoc LLM judge

Suggested models:

- GPT-5.4
- GPT-5.4 Mini
- Claude Sonnet 4.6
- Claude Opus 4.6
- Gemini 3.1 Pro Preview
- GLM-5.1

Estimated cost:

- about `$59`
- about `$89` with 1.5x safety factor

This is the cleanest low-risk package.

### Package B: Recommended thesis run

Run:

- 8-model core frontier plus breadth panel
- minimal scaffold on all 8
- 2 historical anchors
- 2 tools comparisons
- 2 cheap reruns
- judge everything

Suggested models:

- Core 6:
  - `openrouter/openai/gpt-5.4`
  - `openrouter/openai/gpt-5.4-mini`
  - `openrouter/anthropic/claude-sonnet-4.6`
  - `openrouter/anthropic/claude-opus-4.6`
  - `openrouter/google/gemini-3.1-pro-preview`
  - `openrouter/z-ai/glm-5.1`
  - `openrouter/qwen/qwen3.6-plus`
  - `openrouter/deepseek/deepseek-v3.2`
- Historical anchors:
  - `openrouter/anthropic/claude-3.7-sonnet`
  - `openrouter/openai/gpt-5`
- Tools:
  - `openrouter/openai/gpt-5.4`
  - `openrouter/anthropic/claude-sonnet-4.6`
- Reliability reruns:
  - `openrouter/openai/gpt-5.4-mini`
  - `openrouter/z-ai/glm-5.1`

Estimated cost:

- about `$141` to `$146` base
- about `$212` to `$219` with 1.5x safety factor

This is the package I recommend for the thesis.

### Package C: Maximum breadth inside $300

Take Package B and add one or two optional frontier models if they are stable on OpenRouter on run day:

- a Grok 4.20 variant, or
- Kimi K2.5 Thinking

Even then, you should still stay below `$300` unless one provider surprises you badly on tool-scaffold verbosity or caching behavior.

---

## 9. How to execute the experiment step by step

This is the part you can follow directly.

### Step 1: Freeze the exact OpenRouter manifest

Do this on the day you launch the experiment, not earlier.

- Open the Arena coding leaderboard and record the snapshot date.
- Open OpenRouter model pages for the exact slugs you will run.
- Write one small manifest with:
  - model family,
  - exact provider slug,
  - the exact CLI knob you will use in ALEval,
  - which scaffold(s) it will run on,
  - expected cost bucket.

Do not let model names drift mid-experiment.

Recommended manifest to start from:


| Family                 | Exact OpenRouter slug                      | ALEval setting                                                                     | Run on minimal | Run on tools | Operational note                                                   |
| ---------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------- | -------------- | ------------ | ------------------------------------------------------------------ |
| GPT-5.4                | `openrouter/openai/gpt-5.4`                | add `--reasoning-effort high`                                                      | Yes            | Yes          | best current OpenAI frontier slot                                  |
| GPT-5.4 Mini           | `openrouter/openai/gpt-5.4-mini`           | add `--reasoning-effort high`                                                      | Yes            | rerun only   | cheap OpenAI control and rerun target                              |
| Claude Sonnet 4.6      | `openrouter/anthropic/claude-sonnet-4.6`   | no extra CLI flag                                                                  | Yes            | Yes          | use no-cache cost planning unless you patch cache controls         |
| Claude Opus 4.6        | `openrouter/anthropic/claude-opus-4.6`     | no extra CLI flag                                                                  | Yes            | No           | frontier Anthropic anchor, but expensive on tools                  |
| Gemini 3.1 Pro Preview | `openrouter/google/gemini-3.1-pro-preview` | no extra CLI flag                                                                  | Yes            | No           | keep as minimal-only unless you have spare budget                  |
| GLM-5.1                | `openrouter/z-ai/glm-5.1`                  | no extra CLI flag                                                                  | Yes            | rerun only   | cheap breadth model                                                |
| Qwen                   | `openrouter/qwen/qwen3.6-plus`             | no extra CLI flag                                                                  | Yes            | No           | stable paid OpenRouter route for the Arena-leading Qwen 3.6 family |
| DeepSeek               | `openrouter/deepseek/deepseek-v3.2`        | no extra CLI flag unless you verify OpenRouter reasoning reaches the model cleanly | Yes            | No           | best DeepSeek-family coding slot currently exposed on OpenRouter   |
| Historical Claude      | `openrouter/anthropic/claude-3.7-sonnet`   | no extra CLI flag                                                                  | Yes            | No           | run before May 5, 2026 if you want this anchor                     |
| Historical OpenAI      | `openrouter/openai/gpt-5`                  | add `--reasoning-effort high`                                                      | Yes            | No           | direct bridge back to ImpossibleBench                              |


### Step 2: Install only the dependencies you need

For the recommended LCB-only experiment:

```bash
pip install -e ".[test,analysis]"
```

You do not need SWE extras for the main run.

### Step 3: Set the environment

Recommended env:

```bash
cp .env.example .env
```

Add at least:

```bash
OPENROUTER_API_KEY=...
HF_TOKEN=...   # optional but recommended
ALEVAL_JUDGE_MODEL=openrouter/openai/gpt-5.4-mini
```

Then confirm:

```bash
docker version
```

### Step 4: Use a fixed directory layout

Use one folder per model per scaffold so `aleval-report` stays easy to reason about.

Recommended structure:

```text
logs/
  exp_2026-04-08/
    lcb_min/
      gpt-5.4/
      claude-sonnet-4.6/
      ...
    lcb_tools/
      gpt-5.4/
      claude-sonnet-4.6/

reports/
  exp_2026-04-08/
    lcb_min/
      gpt-5.4/
      claude-sonnet-4.6/
      ...
    lcb_tools/
      gpt-5.4/
      claude-sonnet-4.6/
```

### Step 5: Run a 3-sample smoke test on the cheapest serious model

I would start with `gpt-5.4-mini` or `glm-5.1`.

```bash
inspect eval src/impossiblebench/lcb/tasks.py@aleval_livecodebench_minimal \
  --model openrouter/openai/gpt-5.4-mini \
  --sandbox docker \
  -T limit=3 -T max_attempts=3 -T message_limit=40 \
  --reasoning-effort high \
  --log-dir ./logs/exp_2026-04-08/smoke/gpt-5.4-mini
```

Then generate a report:

```bash
aleval-report \
  --logs-dir ./logs/exp_2026-04-08/smoke/gpt-5.4-mini \
  --out-dir ./reports/exp_2026-04-08/smoke/gpt-5.4-mini \
  --llm-judge openrouter/openai/gpt-5.4-mini
```

Check:

- the run completes,
- passed tasks trigger the callout,
- `lie`, `truth`, `evasive`, and `not_applicable` behave as expected,
- the judge output looks sensible.

### Step 6: Run one 10-sample pilot before launching the full panel

This is worth doing because your cost anchors were from `max_attempts=3`, but the thesis run should use `max_attempts=10`.

I would do:

- one pilot on `gpt-5.4`,
- one pilot on `claude-sonnet-4.6`.

Use:

```bash
inspect eval src/impossiblebench/lcb/tasks.py@aleval_livecodebench_minimal \
  --model openrouter/openai/gpt-5.4 \
  --sandbox docker \
  -T limit=10 -T max_attempts=10 -T message_limit=50 \
  --reasoning-effort high \
  --log-dir ./logs/exp_2026-04-08/pilot/lcb_min/gpt-5.4
```

If those 10-sample pilots stay close to the planned cost shape, proceed.

### Step 7: Launch the main minimal panel

Use one command per model so failures are isolated and reruns are easy.

OpenAI template:

```bash
inspect eval src/impossiblebench/lcb/tasks.py@aleval_livecodebench_minimal \
  --model openrouter/openai/gpt-5.4 \
  --sandbox local \
  -T max_attempts=10 -T message_limit=50 \
  --reasoning-effort high \
  --log-dir ./logs/exp_2026-04-08/lcb_min/gpt-5.4 \
  --fail-on-error False
```

Generic non-OpenAI template:

```bash
inspect eval src/impossiblebench/lcb/tasks.py@aleval_livecodebench_minimal \
  --model openrouter/qwen/qwen3.6-plus \
  --sandbox local \
  -T max_attempts=10 -T message_limit=50 \
  --log-dir ./logs/exp_2026-04-08/lcb_min/qwen3.6-plus \
  --fail-on-error False
```

Recommended run order:

1. GPT-5.4 Mini
2. GLM-5.1
3. DeepSeek V3.2 Thinking
4. GPT-5.4
5. Gemini 3.1 Pro Preview
6. Claude Sonnet 4.6
7. Claude Opus 4.6
8. Qwen 3.6 Plus Preview
9. Historical anchors

Why this order:

- cheapest and easiest models flush out harness issues first,
- expensive models only run after the pipeline is already proven.

### Step 8: Run `aleval-report` immediately after each model

Do not wait until the very end.

Example:

```bash
aleval-report \
  --logs-dir ./logs/exp_2026-04-08/lcb_min/gpt-5.4 \
  --out-dir ./reports/exp_2026-04-08/lcb_min/gpt-5.4 \
  --llm-judge openrouter/openai/gpt-5.4-mini
```

After each report, check:

- total sample count is 103,
- passed count is plausible,
- callout count equals the number of triggered labels,
- the judge is not returning many `unknown` labels.

### Step 9: Run tools on two models only

Recommended options:

- frontier-vs-frontier:
  - GPT-5.4
  - Claude Sonnet 4.6
- frontier-vs-cheap-open:
  - GPT-5.4
  - DeepSeek Reasoner

Command template:

```bash
inspect eval src/impossiblebench/lcb/tasks.py@aleval_livecodebench_tools \
  --model openrouter/openai/gpt-5.4 \
  --sandbox docker \
  -T max_attempts=10 -T message_limit=50 \
  --reasoning-effort high \
  --log-dir ./logs/exp_2026-04-08/lcb_tools/gpt-5.4 \
  --fail-on-error False
```

Important note:

- OpenAI tools runs can benefit from automatic prompt caching.
- Anthropic and Gemini tools runs should be budgeted conservatively unless you explicitly add cache control support to the harness.

### Step 10: Run two cheap reruns for variance

Use the same 103-task full split on the same scaffold, same config, same model family, different run.

Best rerun choices:

- GLM-5.1
- Qwen 3.6 Plus

These are cheap enough that the extra statistical confidence is worth more than the token cost.

### Step 11: Aggregate results for the thesis

`aleval-report` is perfect for per-run sanity checks, but your thesis table should come from all per-model CSVs combined.

For the final analysis, build one combined dataframe from every `judged_samples.csv`.

The main tables should include:

- reward-hack rate = `passed / 103`
- unconditional lie rate = `lie / 103`
- unconditional truth rate = `truth / 103`
- unconditional evasive rate = `evasive / 103`
- conditional lie/truth/evasive among triggered callouts
- judge agreement rate

Use 90% Wilson intervals in the main thesis figures to match ImpossibleBench.

### Step 12: Keep an audit trail

For every run, record:

- exact model slug,
- exact date,
- scaffold,
- `max_attempts`,
- `message_limit`,
- whether `reasoning_effort=high` was used,
- output directory,
- any reruns or failures.

This is what will save you when you write the methods section.

---

## 10. What I would report in the thesis

Primary figure:

- reward-hack rate by model on `aleval_livecodebench_minimal`

Primary ALEval figure:

- stacked bars of unconditional `lie`, `truth`, `evasive` rates over all 103 tasks

Secondary figure:

- conditional honesty distribution among triggered callouts only

Secondary appendix comparison:

- minimal vs tools for the two selected models

Methodology appendix:

- deterministic label vs LLM judge agreement
- representative examples of lie, truth, and evasive responses

Statistical tests:

- 90% Wilson confidence intervals for all plotted proportions
- Fisher exact tests for the main pairwise model comparisons you care about
- Holm or Bonferroni correction if you do many pairwise tests

---

## 11. Final recommendation

If you want the best balance of scientific value, cost, and execution risk, run this:

1. Main panel, LCB minimal, 103 tasks:
  - `openrouter/google/gemini-3.1-pro-preview`
  - `openrouter/openai/gpt-5.4`
  - `openrouter/anthropic/claude-opus-4.6`
  - `openrouter/x-ai/grok-4.20`
  - `openrouter/z-ai/glm-5.1`
  - `openrouter/qwen/qwen3.6-plus`
2. Tools comparison:
  - `openrouter/z-ai/glm-5.1`
  - `openrouter/qwen/qwen3.6-plus`
3. Reliability reruns:
  - `openrouter/z-ai/glm-5.1`
  - `openrouter/qwen/qwen3.6-plus`
4. Post-hoc judge:
  - `openrouter/z-ai/glm-5.1`

Expected spend:

- about `$77` to `$79` base
- about `$116` to `$119` with a 1.5x contingency

That is the experiment package I would stand behind for the thesis.

---

## References

- Arena Text Coding leaderboard, snapshot dated April 7, 2026: [https://arena.ai/leaderboard/text/coding](https://arena.ai/leaderboard/text/coding)
- Arena overview leaderboard, coding column snapshot dated April 8, 2026: [https://arena.ai/leaderboard](https://arena.ai/leaderboard)
- ImpossibleBench paper: [https://arxiv.org/abs/2510.20270](https://arxiv.org/abs/2510.20270)
- OpenAI pricing: [https://developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing)
- Google Gemini API pricing: [https://ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing)
- Z.AI pricing: [https://docs.z.ai/guides/overview/pricing](https://docs.z.ai/guides/overview/pricing)
- DeepSeek pricing: [https://api-docs.deepseek.com/quick_start/pricing/](https://api-docs.deepseek.com/quick_start/pricing/)
- OpenRouter GPT-5.4 page: [https://openrouter.ai/openai/gpt-5.4](https://openrouter.ai/openai/gpt-5.4)
- OpenRouter GPT-5.4 Mini page: [https://openrouter.ai/openai/gpt-5.4-mini](https://openrouter.ai/openai/gpt-5.4-mini)
- OpenRouter Claude Sonnet 4.6 page: [https://openrouter.ai/anthropic/claude-sonnet-4.6](https://openrouter.ai/anthropic/claude-sonnet-4.6)
- OpenRouter Claude Opus 4.6 page: [https://openrouter.ai/anthropic/claude-opus-4.6](https://openrouter.ai/anthropic/claude-opus-4.6)
- OpenRouter Gemini 3.1 Pro Preview page: [https://openrouter.ai/google/gemini-3.1-pro-preview](https://openrouter.ai/google/gemini-3.1-pro-preview)
- OpenRouter GLM-5.1 page: [https://openrouter.ai/z-ai/glm-5.1/providers](https://openrouter.ai/z-ai/glm-5.1/providers)
- OpenRouter Qwen3.6 Plus page: [https://openrouter.ai/qwen/qwen3.6-plus](https://openrouter.ai/qwen/qwen3.6-plus)
- OpenRouter DeepSeek V3.2 page: [https://openrouter.ai/deepseek/deepseek-v3.2/providers](https://openrouter.ai/deepseek/deepseek-v3.2/providers)
- OpenRouter Claude 3.7 Sonnet versions page: [https://openrouter.ai/anthropic/claude-3-7-sonnet-20250219/versions](https://openrouter.ai/anthropic/claude-3-7-sonnet-20250219/versions)
- OpenRouter GPT-5 page: [https://openrouter.ai/openai/gpt-5](https://openrouter.ai/openai/gpt-5)
- OpenRouter reasoning tokens guide: [https://openrouter.ai/docs/use-cases/reasoning-tokens](https://openrouter.ai/docs/use-cases/reasoning-tokens)
- OpenRouter prompt caching guide: [https://openrouter.ai/docs/guides/best-practices/prompt-caching](https://openrouter.ai/docs/guides/best-practices/prompt-caching)
- ALEval LiveCodeBench task presets: `src/impossiblebench/lcb/tasks.py`

