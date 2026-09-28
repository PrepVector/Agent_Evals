"""
Small shared helpers for the Gemini version of the workshop.

Two things live here so the three files that call the model
(agent.py, app.py, judge.py) stay short and readable:

1. MODEL_CANDIDATES -- the ONE place to change which Gemini model is used.
2. generate_with_retry() -- calls the API and automatically waits/retries
   when you hit the free tier's rate limit.

Why retries matter: Gemini's free tier allows only a handful of requests
per minute (roughly 5-15, and it varies by account/model). An agent run
makes several calls back to back, and Exercise 1 loops over 15-20 test
cases, so you WILL occasionally see a "429 / rate limit" error. That's
normal on the free tier -- this helper just waits and tries again.

Requires: pip install google-genai
Requires: GEMINI_API_KEY environment variable (free key from
https://aistudio.google.com/apikey -- no credit card needed).
"""

import os
import time

from google import genai
from google.genai import errors

# Tried in order. If a name isn't available to your account (404 / not
# found), the next one is tried automatically, and the first one that
# works is remembered for the rest of the session. Edit this list if
# Google renames or retires a model.
MODEL_CANDIDATES = [
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]

# Seconds to wait between retries when rate limited (free tier limits are
# per-minute, so the later waits are long enough for the window to reset).
RETRY_WAITS = [6, 12, 24, 48, 60]

_working_model = None  # set to the first model that succeeds


def make_client():
    """Create a Gemini client from the GEMINI_API_KEY environment variable."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No API key found. Set GEMINI_API_KEY (get a free key at "
            "https://aistudio.google.com/apikey)."
        )
    return genai.Client(api_key=api_key)


def generate_with_retry(client, contents, config=None):
    """Call client.models.generate_content, retrying on rate limits.

    - 429 (rate limit) and 503 (temporarily overloaded): wait and retry.
    - 404 (model name not available): try the next name in MODEL_CANDIDATES.
    - Anything else (bad key, invalid request, ...): raised immediately.
    """
    global _working_model
    models = [_working_model] if _working_model else list(MODEL_CANDIDATES)

    last_error = None
    for model in models:
        model_not_found = False
        for attempt, wait in enumerate([0] + RETRY_WAITS):
            if wait:
                print(f"  [rate limited on the free tier -- waiting {wait}s, then retrying "
                      f"(attempt {attempt + 1}/{len(RETRY_WAITS) + 1})]")
                time.sleep(wait)
            try:
                response = client.models.generate_content(
                    model=model, contents=contents, config=config
                )
                _working_model = model
                return response
            except errors.APIError as e:
                last_error = e
                if e.code in (429, 503):
                    continue  # wait and retry the same model
                if e.code == 404:
                    model_not_found = True
                    break  # this model name isn't available; try the next one
                raise
        if not model_not_found:
            break  # retries used up on a working model -- stop here, don't cascade
    raise RuntimeError(
        f"Gemini API call failed after retries/fallbacks. Last error: {last_error}\n"
        "If this says quota/rate limit, wait a minute and try again (free tier), "
        "or check your usage at https://aistudio.google.com."
    )
