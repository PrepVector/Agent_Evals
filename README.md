# Agent_Evals

Hands-on materials for the workshop **Evaluating AI Agents: Trajectories, Tools, and Harness Design**.

Pick the folder that matches the model you'll use. The two folders have the same exercises, data, and traces; only the model calls differ.

| If you have... | Use this folder |
|---|---|
| Anthropic API credits | [`workshop_demo_claude/`](workshop_demo_claude/) |
| No paid credits (Gemini has a free tier, no credit card) | [`workshop_demo_gemini/`](workshop_demo_gemini/) |

## Prerequisites

- **Basic Python.** You can read and write functions, loops, lists, and dictionaries. No machine-learning background needed.
- **A Google account** (free). We work in Google Colab notebooks in your browser, so there is nothing to install.
- **An API key for one model provider.** Create it before the workshop; it takes a few minutes.
  - *Free option:* a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey). No credit card needed. The free tier has tight rate limits, so some steps pause for a moment. Free access can depend on your country; if you can't get a key, use Claude instead.
  - *Or:* an Anthropic (Claude) API key with credits.
- **A laptop** with a modern browser (Chrome recommended) and a stable internet connection.
- *Nice to have, not required:* you have called an LLM API or built something with a chat model before. All the code is provided.

All data in the workshop is synthetic. You do not need any company or personal data.

**5-minute check before the session:** create your key, then open [colab.research.google.com](https://colab.research.google.com) and confirm you can create a new notebook.

Each folder has its own README with setup steps.
