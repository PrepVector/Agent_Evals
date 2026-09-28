"""
Shared example app for Exercises 1 and 2: a single-turn RAG QA bot.

Answers questions using the same synthetic "Voltaic Labs" knowledge base
as the Section 6 research agent (see research_agent/fixtures.py) --
reused here, unmodified, so participants aren't learning a new domain
partway through the workshop.

Unlike the Section 6 agent, this app is single-turn and has no tools:
all documents are stuffed into the prompt as context, and the model
answers directly. That's intentional -- Exercises 1 and 2 are about
input/output evals, not trajectories; the agent/harness distinction
is exactly what Section 6 exists to teach.

Requires: pip install anthropic
Requires: ANTHROPIC_API_KEY environment variable.
"""

import sys

import anthropic

# Reuses the exact same fixture data as the Section 6 harness.
sys.path.insert(0, "../research_agent")
from fixtures import PAGE_CONTENT as _ALL_DOCS, AGENT_ONLY_URLS  # noqa: E402


# The Q&A bot's knowledge base: every fixture document except the ones that
# exist only to test the Section 6 agent.
PAGE_CONTENT = {url: text for url, text in _ALL_DOCS.items() if url not in AGENT_ONLY_URLS}

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = (
    "You are a Q&A assistant for Voltaic Labs. Answer the user's question "
    "using ONLY the context documents provided below. Cite the URL of the "
    "document(s) you used. If the context doesn't contain enough "
    "information to answer confidently, say so directly instead of "
    "guessing.\n\n"
    "--- CONTEXT DOCUMENTS ---\n\n"
    + "\n\n".join(f"[{url}]\n{text}" for url, text in PAGE_CONTENT.items())
)


def answer_question(question: str) -> str:
    """Ask the QA bot a single question and return its answer text."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question}],
    )
    return "".join(b.text for b in response.content if b.type == "text")


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What is Voltaic Labs' most recent energy density figure?"
    print(f"Q: {q}\n")
    print(f"A: {answer_question(q)}")
