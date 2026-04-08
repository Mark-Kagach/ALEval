# ALEval experiment report: Arena-aligned models, sample sizes, and cost estimates

This document turns the agreed LiveCodeBench-only experiment plan into a concrete briefing: which coding models to prioritize given public leaderboard signals, how many examples to run per model, and order-of-magnitude API costs. It does **not** execute evaluations.

**Scope:** LiveCodeBench impossible tasks, `split=conflicting`, presets `aleval_livecodebench_minimal` and (optionally) `aleval_livecodebench_tools`. SWE-bench is out of scope for cost reasons.

---

## 1. Leaderboard context (Code Arena, Apr 2026 snapshot)

The [Code AI Leaderboard](https://arena.ai/leaderboard/code) (Arena-style coding benchmark, **224,709 votes**, **59 models**, snapshot **Apr 1, 2026**) ranks models by Elo-style scores on **agentic coding** (multi-step reasoning and tool use). At that snapshot:

| Rank band | Pattern (org) | Takeaway for ALEval |
|-----------|----------------|----------------------|
| 1–5 | **Anthropic** dominates the very top | Strong candidates: **Opus / Sonnet** family (frontier coding). |
| ~5–7 | **OpenAI**, **Google**, **Alibaba** | Strong candidates: **GPT-5 / o3 / o4-mini**, **Gemini**, **Qwen** coding variants. |
| ~8–12 | **Z.ai**, **Google**, **Xiaomi**, **Moonshot**, **MiniMax**, **OpenAI** | Good “breadth” slots: **GLM**, **Kimi**, **MiniMax**, additional **GPT** variants—**if** your Inspect + billing stack supports them. |
| Mid / lower | **DeepSeek**, **Alibaba** open-weight, **xAI**, **Mistral**, etc. | Useful for **open vs closed** and **cost baselines**—not always at the top of Arena but often strong on code. |

Exact **model names** on the public page are sometimes abbreviated; treat Arena as a **prior** for which *labs* and *families* matter, then map to **concrete API model IDs** in Inspect (e.g. `openai/gpt-5-2025-08-07`, `anthropic/claude-sonnet-4-20250514`) at run time—IDs change with releases.

---

## 2. Recommended model set (broad but actionable)

Below is an **informative** set that mirrors Arena diversity (top proprietary labs + strong open/API models + reasoning vs non-reasoning). Replace version strings with whatever Inspect lists for your run date.

### Tier S — Arena top band (proprietary, coding-first)

| Role | Representative Inspect-style IDs (verify before running) | Notes |
|------|----------------------------------------------------------|--------|
| Anthropic flagship | `anthropic/claude-opus-4-1-20250805`, `anthropic/claude-sonnet-4-20250514` | Arena cluster at ranks 1–4 in the Apr 2026 snapshot; Opus is **expensive**. |
| OpenAI flagship + reasoning | `openai/gpt-5-2025-08-07`, `openai/o3`, `openai/o4-mini` | GPT-5 and o3 match ImpossibleBench-style reporting; o4-mini is a **cheap** control. |
| Google | `google/gemini-2.5-pro-preview-06-05` (example—pin current ID) | Strong Arena placement; confirm sandbox + Inspect support. |

### Tier A — Breadth (still frontier, different labs)

| Role | Representative IDs | Notes |
|------|---------------------|--------|
| Alibaba coding | `openrouter/qwen/qwen3-coder-480b-a35b-instruct` or provider-specific Qwen3-Coder | Arena top-10 band; may need OpenRouter or native API. |
| Prior Sonnet (ablation) | `anthropic/claude-3-7-sonnet-20250219` | Same lab, older generation—useful **paired** comparison with Sonnet 4. |
| OpenAI generalist | `openai/gpt-4.1` | Not always top of Arena coding today but good **non-reasoning** baseline next to GPT-5. |

### Tier B — Open / efficient (Arena mid-tier but paper-relevant)

| Role | Representative IDs | Notes |
|------|---------------------|--------|
| DeepSeek | `openrouter/deepseek/deepseek-chat` or DeepSeek-V3 API | Strong code, MIT license family; pricing often low. |
| Additional open | Qwen / Mistral / Kimi via OpenRouter | Only if you need extra **open-weight** points—validate Inspect integration first. |

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

| Preset | Reported total tokens (5 samples) | × 103/5 → full split scale |
|--------|-----------------------------------|-----------------------------|
| `aleval_livecodebench_minimal` | **45,871** | **≈ 945,144** |
| `aleval_livecodebench_tools` | **509,278** | **≈ 10,491,127** |

Per-sample (minimal) token **components** in your log (5-sample aggregate):  
**I = 9,730**, **O = 36,141**, **R = 32,384** (reasoning).  
Inspect’s single “total” line is **not** always equal to I + O + R; **billing** follows provider rules (input / output / cached / reasoning).

**Tools run** (5-sample aggregate): **I = 92,366**, **O = 27,664**, **CR = 389,248**, **R = 13,952** — tools are **~11×** the minimal total tokens in your data; **cache-read** lines can dominate cost depending on price.

### 4.2 OpenAI GPT-5-class minimal run (illustrative)

Using **scaled I/O** from your minimal run to 103 tasks:

- **Input tokens** ≈ 9,730 × (103/5) = **200,438**  
- **Output + reasoning** (if both billed as output tier): (36,141 + 32,384) × (103/5) = **1,411,655**

At illustrative **$2 / 1M input** and **$8 / 1M output** (check current OpenAI pricing; reasoning may differ):

| Component | Tokens | Cost @ $2/$8 |
|-----------|--------|----------------|
| Input | ~0.200M | ~$0.40 |
| Output-side (O+R) | ~1.412M | ~$11.30 |
| **Total (order of magnitude)** | — | **~$12** per model per minimal full run |

This is **one** model; other labs multiply by their **list prices** and token profiles (Opus: high $/token; DeepSeek: often much lower).

### 4.3 Tools scaffold (illustrative, GPT-5-class)

Scaling your **509,278** total tokens by 103/5 gives **~10.5M** reported-token-equivalents per full tools run for the same model class—**roughly an order of magnitude more expensive** than minimal for the same 103 tasks, before accounting for **cache-read** discounts.

**Conservative planning:** budget **~8–15×** the minimal per-model cost for a **full** tools run vs minimal for the **same** model (depends on cache pricing).

### 4.4 LLM judge (`aleval-report --llm-judge`)

Callouts are a **subset** of 103 (only passed tasks). Judge cost is usually **small** vs agent loops if you use a mid-tier judge (e.g. GPT-4.1-class)—on the order of **$1–15** for all callouts across all models in a single report batch, unless you judge with a flagship model on huge text.

---

## 5. Scenario budgets (all numbers are estimates)

Assume **103 tasks per model** for minimal unless noted. Dollar ranges use the **~$12/minimal/model** anchor for **GPT-5-class** OpenAI pricing; **multiply** for Opus (often **2–4×**), **reduce** for o4-mini / DeepSeek / Qwen API.

| Scenario | What you run | Models (count) | Minimal cost tier | Tools extra | Judge (order of magnitude) | **Total ballpark** |
|----------|----------------|----------------|-------------------|-------------|----------------------------|----------------------|
| **A — Core paper table** | Minimal only, full 103 | 6–8 | 6–8 × ~$8–25 = **$48–200** | — | **$2–10** | **~$50–220** |
| **B — Core + reliability** | A + **2nd run** on 2 cheap models | +2 × 2 models × ~$8–15 | **+$32–60** | — | — | **+$30–60** on top of A |
| **C — Tools comparison** | Full 103 tools on **2** Arena-top models | 2 | — | 2 × ~$80–180 (high variance) | — | **+$160–360** (can dominate budget) |
| **D — Tools subsample** | Tools on **34** tasks (⅓), 2 models | 2 | — | ~⅓ of C | — | **~$50–120** |

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
- ALEval presets: [`src/impossiblebench/lcb/tasks.py`](../src/impossiblebench/lcb/tasks.py).  
- ImpossibleBench paper (reward-hack rates, model list): [arXiv:2510.20270](https://arxiv.org/pdf/2510.20270).
