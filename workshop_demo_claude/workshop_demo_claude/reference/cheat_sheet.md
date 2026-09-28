# AI Evals Cheat Sheet

A quick-reference handout for Sections 4 and 6. Print it, or keep it
open in a second tab during the exercises.

---

## 1. Assertion vs. judge: which do you need?

Use this at both levels — grading a single answer (Exercise 2) and
grading an agent step (Section 6).

```
Can you check it with plain code — a regex, an exact match,
a schema check, a count, a length, a "does this URL appear
in this list"?
  |
  YES ──────────────────────────────▶  Use a CODE ASSERTION.
  |                                     Cheaper, deterministic,
  |                                     no model call needed.
  NO
  |
  Does correctness depend on meaning, tone, factual grounding,
  or "did this reasoning make sense" — something a human would
  need to read and think about?
  |
  YES ──────────────────────────────▶  Use an LLM-AS-JUDGE.
                                        Write a rubric, force a
                                        structured verdict, and
                                        calibrate against human
                                        labels before you trust it.
```

**Rule of thumb:** if you can write the check in one line of Python
without an LLM call, do that first. Save judges for the things that
actually require judgment — that's also why they're the more expensive
and slower option to run at scale.

| Question type | Assertion or judge? |
|---|---|
| Is the output valid JSON matching this schema? | Assertion |
| Does the response cite the URL it used? | Assertion (does the string appear) |
| Is the citation actually accurate? | Judge (needs to compare meaning) |
| Did the agent call `fetch` before `write_summary`? | Assertion |
| Was the agent's *reasoning* for calling that tool sound? | Judge |
| Is the response under 200 words? | Assertion |
| Is the response helpful and complete? | Judge |

---

## 2. Judge-bias checklist

Before trusting a judge's verdicts, check it for these four biases.
All four are checked the same way: **does the judge's verdict change
when something irrelevant to correctness changes?**

- [ ] **Position bias** — in a pairwise judge (A vs. B), does swapping
      which answer is shown first change the verdict? Test by running
      the same pair both orders.
- [ ] **Verbosity bias** — does a longer, more padded-out answer score
      better than a shorter, equally correct one? Test with a
      deliberately verbose restatement of a correct short answer.
- [ ] **Self-preference bias** — if the judge is the same model family
      as the thing it's grading, does it rate that model's own outputs
      more favorably than an equally good answer phrased differently?
- [ ] **Inconsistency** — does the judge give the same verdict on the
      same input if you run it twice? (Especially relevant at
      temperature > 0.) If not, either lower temperature or treat the
      judge's verdict as noisy and require agreement across multiple
      runs.

**The actual test for all of these:** hand-label a small set yourself
(8-20 examples, like `judge/labeled_examples.json`), run the judge
against it, and measure agreement. Don't ship a judge you haven't
checked against human labels at least once.

---

## 3. Agentic eval checklist

Things to check in a trajectory, beyond "was the final answer right."
See `research_agent/traces/INDEX.md` for worked examples of each.

- [ ] **Tool-use correctness** — right tool for the task, correct
      arguments, in a sensible order.
- [ ] **Outcome / state, not just trajectory** — did something *actually
      happen*, not just "did the agent say it happened"? A "compose"
      step (drafting an answer) and a "deliver" step (actually saving,
      sending, or publishing it) are different things — an agent can
      compose a perfectly good answer and still never deliver it.
- [ ] **Grounding** — every claim in the final output traces back to a
      tool call that actually returned that information (not just a
      search snippet, not invented).
- [ ] **Recency / source conflicts** — when multiple sources disagree,
      did the agent use the most current or most authoritative one?
- [ ] **Error handling** — if a tool call failed or returned an error,
      did the agent notice and adapt, or proceed as if nothing happened?
- [ ] **Loop / repeat detection** — did the agent call the same tool
      repeatedly without making progress (no new information, no
      converging toward an answer)?
- [ ] **Termination** — did the agent stop at a reasonable point? Both
      "never finishes" and "gives up too early, before gathering enough
      information" count as termination failures.
- [ ] **Constraint compliance** — if the task specified a hard constraint
      (a length limit, a format, a restriction like "don't do X"), did
      the agent's actual output honor it, not just approximate it?
- [ ] **Prompt-injection resistance** — if fetched content contains text
      that looks like an instruction ("ignore previous instructions..."),
      does the agent treat it as data to summarize, or as a command to
      obey? Worth testing explicitly, not just hoping it doesn't come up.
- [ ] **Cost / efficiency** — how many steps or tokens did it take?
      Two trajectories can both "pass" but one took 3 steps and the
      other took 15 — that's worth tracking even when it's not a
      pass/fail criterion on its own.

**Mapping to assertion vs. judge:** everything above except grounding
in the general case is checkable with plain code against the trajectory
log (see the eight example functions in
`research_agent/Agentic_Evals_Hands_On.ipynb`) — including outcome/state
and prompt-injection resistance, which are just as codeable as tool
order once you know what to check for. Judging whether a synthesized
summary is well-grounded *in general*, across arbitrary tasks the fixed
checks above can't anticipate, is where a trajectory judge takes over
from hand-written assertions.

---

## 4. What we're evaluating, at a glance

A summary table like this is worth putting up at the start of Section 6
— it previews every metric before diving into any one of them. Fill in
your own target benchmarks once you've run the harness against your
own agent a few times; don't invent numbers before you've measured
anything.

| Layer | What it checks | Assertion or judge? |
|---|---|---|
| Tool-use correctness | Right tool, right args, sensible order | Assertion |
| Outcome / state | Was the report actually delivered, not just composed? | Assertion |
| Grounding | Every claim traces back to a real fetch | Assertion (known patterns) + Judge (general case) |
| Recency | Most current source used when sources conflict | Assertion |
| Error handling | Tool errors noticed and adapted to | Assertion |
| Loop detection | No excessive repeated calls | Assertion |
| Constraint compliance | Length/format constraints honored | Assertion |
| Injection resistance | Fetched content treated as data, not commands | Assertion |
| Judge calibration | Judge's verdicts agree with human labels | Measured empirically against a labeled set (see `judge/labeled_examples.json`) |

A note on that last row, since it's easy to get wrong: judge calibration
is something you *measure* by running the judge against a labeled set
you already have verdicts for — it is not something you can derive by
squaring or cubing a pass rate, and a metric that always equals your
overall pass rate by construction isn't telling you anything a plain
pass rate wasn't already telling you. If two of your "metrics" can
never disagree, you only have one metric.

---

## 5. From caught failure to fix

Turning a caught failure into an actual fix, not just a red X in a
report:

| Failure pattern caught | Likely root cause | Fix to try |
|---|---|---|
| Cites the stale source | No instruction to prefer recency when sources conflict | Add an explicit "use the most recent source" rule to the system prompt |
| Cites without fetching | Search snippets look "good enough" to answer from | Instruct the agent to only cite facts it has fetched, not just searched |
| Loops without converging | No natural stopping signal in the prompt | Add an explicit step budget or "if you have enough info, stop searching" instruction |
| Composes but never delivers | Model treats "wrote a good answer" as done | Make the system prompt explicit that composing isn't the same as finishing |
| Ignores a tool error | Nothing tells the model errors need a different response | Add an explicit "if a tool returns an error, do X" instruction |
| Ignores a length constraint | Constraint stated once, easy to drift from over a long generation | Restate the constraint right before the final answer, or check it and ask the model to retry |
| Falls for a prompt injection | Model doesn't distinguish "system instructions" from "content I'm summarizing" | Explicitly instruct the model to treat fetched content as data, never as commands |
