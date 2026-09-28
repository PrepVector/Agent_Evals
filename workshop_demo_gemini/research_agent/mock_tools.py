"""
Mock tools for the research agent harness.

Each tool is a plain Python function with no real network calls -- they
read from the fixture data in fixtures.py. This is what makes the harness
safe and fast to run repeatedly in a workshop setting: no API costs for
search/fetch, no real side effects, fully deterministic.

To add a new mock tool (for the "build your own mock tool" hands-on
step), follow this same pattern:
  1. Write a plain function that takes simple arguments and returns a
     JSON-serializable result.
  2. Add a matching entry to TOOL_SCHEMAS below, describing it for the
     model.
  3. Add it to TOOL_FUNCTIONS so the agent loop can dispatch to it.
"""

from fixtures import SEARCH_INDEX, PAGE_CONTENT

# In-memory scratchpad for take_note(). Reset at the start of every run.
_notes = []


def reset_state():
    """Call this before each new agent run so notes and delivered
    reports don't leak across runs."""
    _notes.clear()
    _DELIVERED_REPORTS.clear()


def search(query: str) -> dict:
    """Keyword search over the fixture index. Very simple: a document
    matches if any query word appears in its title, tags, or snippet."""
    words = [w.lower() for w in query.split() if len(w) > 2]
    results = []
    for doc in SEARCH_INDEX:
        haystack = " ".join([doc["title"], " ".join(doc["tags"]), doc["snippet"]]).lower()
        if any(w in haystack for w in words):
            results.append({"url": doc["url"], "title": doc["title"], "snippet": doc["snippet"]})
    return {"results": results[:6]}


def fetch(url: str) -> dict:
    """Return the full page content for a URL, if it exists in the fixtures."""
    if url in PAGE_CONTENT:
        return {"url": url, "content": PAGE_CONTENT[url]}
    return {"url": url, "error": "404: no such page in this harness"}


def take_note(note: str) -> dict:
    """Append a note to the agent's scratchpad. Useful for trajectory
    checks like 'did it note the source before citing it'."""
    _notes.append(note)
    return {"ok": True, "notes_so_far": len(_notes)}


def write_summary(summary: str) -> dict:
    """Compose the final summary. NOT terminal -- the agent must follow
    this with save_report to actually finish the task. This mirrors a
    real pipeline: compose, then deliver."""
    return {"ok": True, "summary": summary}


_DELIVERED_REPORTS = {}


def save_report(doc_id: str, summary: str) -> dict:
    """Terminal tool: deliver the composed summary. The agent loop treats
    a call to save_report as the end of the run. This is a mocked
    'outcome/state' check -- unlike write_summary (did the agent produce
    text?), this checks whether a report was actually delivered/persisted,
    the same distinction real_agent.save_to_drive vs write_doc draws."""
    _DELIVERED_REPORTS[doc_id] = summary
    return {"ok": True, "doc_id": doc_id, "delivered": True}


def report_was_delivered(doc_id: str) -> bool:
    """Outcome-state check: did save_report actually persist this doc_id?
    (Not part of the agent's tool surface -- used by graders/tests.)"""
    return doc_id in _DELIVERED_REPORTS


TOOL_SCHEMAS = [
    {
        "name": "search",
        "description": "Search a small internal knowledge base for documents matching a query.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search keywords"}},
            "required": ["query"],
        },
    },
    {
        "name": "fetch",
        "description": "Fetch the full content of a page by URL (get the URL from search results first).",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "URL returned by search"}},
            "required": ["url"],
        },
    },
    {
        "name": "take_note",
        "description": "Save a short note to your scratchpad for later reference. Use this to record a fact plus the URL it came from, before citing it.",
        "input_schema": {
            "type": "object",
            "properties": {"note": {"type": "string"}},
            "required": ["note"],
        },
    },
    {
        "name": "write_summary",
        "description": "Compose your final answer, with citations. This does NOT end the task -- you must follow it with save_report to actually deliver the report.",
        "input_schema": {
            "type": "object",
            "properties": {"summary": {"type": "string", "description": "The final summary, with citations"}},
            "required": ["summary"],
        },
    },
    {
        "name": "save_report",
        "description": "Deliver the composed summary and end the task. Call this exactly once, after write_summary, when you're done researching.",
        "input_schema": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "string", "description": "A short id for this report, e.g. 'voltaic_energy_density'"},
                "summary": {"type": "string", "description": "The same final summary you composed with write_summary"},
            },
            "required": ["doc_id", "summary"],
        },
    },
]

TOOL_FUNCTIONS = {
    "search": search,
    "fetch": fetch,
    "take_note": take_note,
    "write_summary": write_summary,
    "save_report": save_report,
}
