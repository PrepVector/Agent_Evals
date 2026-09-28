# Research agent harness (Section 6)

A small research agent + mock-tool harness for the agentic evals section.
No real web access, no production data — you'll run it with your own
`ANTHROPIC_API_KEY`.

## Files

- `fixtures.py` — a synthetic knowledge base about a fictional battery
  startup ("Voltaic Labs"). All content is invented.
- `mock_tools.py` — five tools the agent can call: `search`, `fetch`,
  `take_note`, `write_summary`, `save_report`. Each is a plain function,
  no network calls.
- `agent.py` — the agent loop. Calls Claude with tool-use, dispatches
  tool calls to the mock tools, and logs every step into a `trajectory`
  dict. The flow is compose-then-deliver: `write_summary` composes the
  answer, `save_report` delivers it and ends the run.
- `traces/` — eight pre-recorded trajectories you'll work with in
  `Agentic_Evals_Hands_On.ipynb`.
- `Agentic_Evals_Hands_On.ipynb` — the hands-on notebook.

## Running the agent yourself

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-...
python agent.py "Write a short summary of Voltaic Labs' battery technology, including their most recent energy density figure, with citations."
```

## Adding your own mock tool

1. Write a plain function in `mock_tools.py`.
2. Add a schema entry to `TOOL_SCHEMAS` describing it for the model.
3. Add it to the `TOOL_FUNCTIONS` dict so the agent loop can dispatch to it.

No changes to `agent.py` are needed — the loop is schema-driven.
