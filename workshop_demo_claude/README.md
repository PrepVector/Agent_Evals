# AI Evals Workshop — Hands-On Materials (Claude version)

This folder has everything you need for the hands-on portions of the
workshop. Each subfolder is self-contained.

> **No Anthropic credits?** There's a free-tier Gemini version of everything
> in this folder at `../workshop_demo_gemini/` — same exercises, same data.

| Folder | What it's for |
|---|---|
| `rag_app/` | Exercise 1 — build a golden eval set |
| `judge/` | Exercise 2 — build and calibrate an LLM-as-judge |
| `research_agent/` | Section 6 — agentic evals, trajectories, and harness design |
| `reference/` | Cheat sheet — assertion-vs-judge, judge-bias, and agentic eval checklists |

## Before you start

You'll need your own Anthropic API key for the exercises that call the
model live (`rag_app`, `judge`, and running `research_agent/agent.py`
yourself). The Section 6 hands-on notebook (`Agentic_Evals_Hands_On.ipynb`)
does **not** need a key — the traces are pre-loaded.

Get a key at [console.anthropic.com](https://console.anthropic.com) if
you don't already have one. Each notebook's first cell has a `PASTE_KEY_HERE`
placeholder — replace it with your key.

## Running the notebooks

Open any `.ipynb` file in Google Colab (File → Upload notebook, or drag
it in), or run it locally with Jupyter. The first cell in each notebook
installs dependencies and pulls in the supporting files from this repo.
