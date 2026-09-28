"""
LLM-as-judge plumbing for Exercise 2.

Judges a (question, answer) pair against a rubric, using Claude's
tool-use API to FORCE a structured verdict rather than free text --
this is the "forcing a structured verdict" technique from Section 4.
The rubric itself is a plain string, passed in by the caller: that's
the part participants write and iterate on, not this file.

Requires: pip install anthropic
Requires: ANTHROPIC_API_KEY environment variable.
"""

import sys

import anthropic

sys.path.insert(0, "../research_agent")
from fixtures import PAGE_CONTENT as _ALL_DOCS, AGENT_ONLY_URLS  # noqa: E402 -- same context the QA bot answered from


# The Q&A bot's knowledge base: every fixture document except the ones that
# exist only to test the Section 6 agent.
PAGE_CONTENT = {url: text for url, text in _ALL_DOCS.items() if url not in AGENT_ONLY_URLS}

MODEL = "claude-sonnet-4-6"

SUBMIT_VERDICT_TOOL = {
    "name": "submit_verdict",
    "description": "Submit your grading verdict for this question/answer pair.",
    "input_schema": {
        "type": "object",
        "properties": {
            "verdict": {
                "type": "string",
                "enum": ["pass", "fail"],
                "description": "pass if the answer meets every rubric criterion, fail if it violates any of them",
            },
            "reasoning": {
                "type": "string",
                "description": "1-2 sentences explaining the verdict, referencing the specific rubric criterion",
            },
        },
        "required": ["verdict", "reasoning"],
    },
}


def judge_answer(question: str, answer: str, rubric: str) -> dict:
    """Grade one (question, answer) pair against `rubric`.

    Returns {"verdict": "pass" | "fail", "reasoning": "..."}.

    tool_choice forces the model to call submit_verdict -- it cannot
    respond with free text instead, which is what makes this usable as
    an automated eval rather than something you have to re-parse by hand.
    """
    client = anthropic.Anthropic()

    context_block = "\n\n".join(f"[{url}]\n{text}" for url, text in PAGE_CONTENT.items())

    system = (
        "You are grading an AI assistant's answer to a question about Voltaic Labs, "
        "using the rubric below. The assistant answered using only the context "
        "documents also shown below -- you have the same documents, so you can "
        "check its claims directly.\n\n"
        f"--- RUBRIC ---\n{rubric}\n\n"
        f"--- CONTEXT DOCUMENTS (what the assistant had access to) ---\n{context_block}"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=system,
        tools=[SUBMIT_VERDICT_TOOL],
        tool_choice={"type": "tool", "name": "submit_verdict"},
        messages=[{"role": "user", "content": f"Question: {question}\n\nAssistant's answer: {answer}"}],
    )

    tool_call = next(b for b in response.content if b.type == "tool_use")
    return tool_call.input


if __name__ == "__main__":
    rubric = (
        "- The answer must be grounded only in the provided context documents.\n"
        "- If sources conflict, the answer should use the most recent one.\n"
        "- The answer must cite the source URL(s) it used.\n"
    )
    q = "What is Voltaic Labs' most recent energy density figure?"
    a = "Voltaic Labs reaches 320 Wh/kg. Source: https://wiki.example/voltaic-labs/press-2022"
    print(judge_answer(q, a, rubric))
