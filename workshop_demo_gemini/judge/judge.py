"""
LLM-as-judge plumbing for Exercise 2.

Judges a (question, answer) pair against a rubric, using Gemini's
function-calling API to FORCE a structured verdict rather than free
text -- this is the "forcing a structured verdict" technique from
Section 4. The rubric itself is a plain string, passed in by the
caller: that's the part participants write and iterate on, not this file.

Requires: pip install google-genai
Requires: GEMINI_API_KEY environment variable (free key from
https://aistudio.google.com/apikey -- no credit card needed).
"""

import sys

from google.genai import types

sys.path.insert(0, "../research_agent")
from fixtures import PAGE_CONTENT as _ALL_DOCS, AGENT_ONLY_URLS  # noqa: E402 -- same context the QA bot answered from
from gemini_helpers import make_client, generate_with_retry  # noqa: E402


# The Q&A bot's knowledge base: every fixture document except the ones that
# exist only to test the Section 6 agent.
PAGE_CONTENT = {url: text for url, text in _ALL_DOCS.items() if url not in AGENT_ONLY_URLS}

SUBMIT_VERDICT_DECLARATION = {
    "name": "submit_verdict",
    "description": "Submit your grading verdict for this question/answer pair.",
    "parameters": {
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

    The tool_config below (mode="ANY" + allowed_function_names) forces the
    model to call submit_verdict -- it cannot respond with free text
    instead, which is what makes this usable as an automated eval rather
    than something you have to re-parse by hand.
    """
    client = make_client()

    context_block = "\n\n".join(f"[{url}]\n{text}" for url, text in PAGE_CONTENT.items())

    system = (
        "You are grading an AI assistant's answer to a question about Voltaic Labs, "
        "using the rubric below. The assistant answered using only the context "
        "documents also shown below -- you have the same documents, so you can "
        "check its claims directly.\n\n"
        f"--- RUBRIC ---\n{rubric}\n\n"
        f"--- CONTEXT DOCUMENTS (what the assistant had access to) ---\n{context_block}"
    )

    config = types.GenerateContentConfig(
        system_instruction=system,
        tools=[types.Tool(function_declarations=[SUBMIT_VERDICT_DECLARATION])],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode="ANY", allowed_function_names=["submit_verdict"]
            )
        ),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    response = generate_with_retry(
        client,
        contents=f"Question: {question}\n\nAssistant's answer: {answer}",
        config=config,
    )

    parts = response.candidates[0].content.parts or []
    call = next(p.function_call for p in parts if p.function_call)
    return dict(call.args)


if __name__ == "__main__":
    rubric = (
        "- The answer must be grounded only in the provided context documents.\n"
        "- If sources conflict, the answer should use the most recent one.\n"
        "- The answer must cite the source URL(s) it used.\n"
    )
    q = "What is Voltaic Labs' most recent energy density figure?"
    a = "Voltaic Labs reaches 320 Wh/kg. Source: https://wiki.example/voltaic-labs/press-2022"
    print(judge_answer(q, a, rubric))
