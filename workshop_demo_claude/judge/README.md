# LLM-as-judge (Exercise 2)

Grades (question, answer) pairs from the Exercise 1 QA bot against a
rubric you write, forcing a structured pass/fail verdict.

## Files

- `judge.py` — `judge_answer(question, answer, rubric)`. The rubric is
  passed in — that's the part you write and iterate on in the notebook.
- `labeled_examples.json` — 8 (question, answer) pairs with human
  verdicts and reasoning, for you to calibrate your judge against.
- `Exercise2_LLM_Judge.ipynb` — the hands-on: read the labeled examples,
  write a rubric, run the judge, measure agreement, iterate.

## Setup

The notebook's first cell handles installation and cloning — just replace
`PASTE_KEY_HERE` with your API key and run it.
