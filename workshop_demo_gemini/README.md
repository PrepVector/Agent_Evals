# AI Evals Workshop — Hands-On Materials (Gemini version)

This is the **Gemini** version of the workshop materials. It is identical
to the Claude version in `../workshop_demo_claude/` except for the model calls —
same exercises, same data, same traces, same checks. Pick whichever you
have access to:

| If you have... | Use this folder |
|---|---|
| Anthropic API credits | `../workshop_demo_claude/` (Claude) |
| No paid credits | **this folder** (Gemini has a free tier, no credit card) |

| Folder | What it's for |
|---|---|
| `rag_app/` | Exercise 1 — build a golden eval set |
| `judge/` | Exercise 2 — build and calibrate an LLM-as-judge |
| `research_agent/` | Section 6 — agentic evals, trajectories, and harness design |
| `reference/` | Cheat sheet — assertion-vs-judge, judge-bias, and agentic eval checklists |

## Before you start

You'll need a **free Gemini API key** for the exercises that call the
model live (`rag_app`, `judge`, and running `research_agent/agent.py`
yourself). The Section 6 hands-on notebook (`Agentic_Evals_Hands_On.ipynb`)
does **not** need a key — the traces are pre-loaded.

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
   and sign in with a Google account.
2. Click **Create API key** — no credit card is required.
3. Each notebook's first cell has a `PASTE_KEY_HERE` placeholder — replace it with your key.

## Things to know about the free tier

- **Rate limits are tight** (roughly 5–15 requests per minute, varying by
  account and model). You may see a "rate limited — waiting…" message; the
  code retries automatically, so just let it run. Runs that make many
  calls (like Exercise 1's test-case loop) can take a few minutes.
- **Data use:** on the free tier, Google may use prompts and responses to
  improve its products. Everything in this workshop is synthetic, but
  don't paste anything sensitive into your own experiments.
- **Availability** of the free tier can depend on your region. If you
  can't get a key working, use the Claude folder instead or ask the
  instructor.
- **Model names change.** The model is set in one place —
  `research_agent/gemini_helpers.py` (`MODEL_CANDIDATES`); if a model is
  unavailable, the next one in the list is tried automatically.

## Running the notebooks

Open any `.ipynb` file in Google Colab (File → Upload notebook, or drag
it in), or run it locally with Jupyter. The first cell in each notebook
installs dependencies and pulls in the supporting files from this repo.
