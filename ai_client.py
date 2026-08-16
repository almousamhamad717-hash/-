import os
import json
import logging
import sys
from time import sleep

import requests
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Configuration from environment
API_KEY = os.getenv("KEY_ONE") or os.getenv("API_KEY")
API_URL = os.getenv("API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent")
# If true, put key in query string as ?key=..., otherwise use Authorization: Bearer
USE_KEY_IN_QUERY = os.getenv("USE_KEY_IN_QUERY", "true").lower() in ("1", "true", "yes")
TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
RETRIES = int(os.getenv("RETRIES", "2"))
BACKOFF_SECONDS = float(os.getenv("BACKOFF_SECONDS", "1.5"))


def ask_ai(prompt_text: str) -> str:
    """Send prompt_text to the configured AI endpoint and return the generated text.

    Returns the generated answer string on success, or raises RuntimeError on failure.
    """
    if not API_KEY:
        raise RuntimeError("API key not found. Set KEY_ONE or API_KEY environment variable.")

    # Build URL and headers
    if USE_KEY_IN_QUERY:
        url = f"{API_URL}?key={API_KEY}"
        headers = {"Content-Type": "application/json"}
    else:
        url = API_URL
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

    # Request body - adapt this to the API you're using
    data = {"contents": [{"parts": [{"text": prompt_text}]}]}

    last_exc = None
    for attempt in range(1, RETRIES + 2):
        try:
            logger.debug("POST %s (attempt %d) - payload=%s", url, attempt, data)
            resp = requests.post(url, headers=headers, json=data, timeout=TIMEOUT)
            logger.debug("Response status=%s", resp.status_code)

            # Raise for HTTP errors
            if resp.status_code != 200:
                logger.warning("Request failed: status=%s, body=%s", resp.status_code, resp.text)
                # If 4xx, do not retry except maybe 429
                if 400 <= resp.status_code < 500 and resp.status_code != 429:
                    raise RuntimeError(f"Request failed: HTTP {resp.status_code}: {resp.text}")
                # otherwise will retry
            else:
                try:
                    json_res = resp.json()
                except ValueError as e:
                    raise RuntimeError(f"Invalid JSON response: {e}")

                # Flexible parsing: try common shapes, fall back to pretty JSON
                # 1) Look for candidates -> content -> parts -> text
                candidates = json_res.get("candidates")
                if candidates and isinstance(candidates, list):
                    answer = (candidates[0].get("content", {}).get("parts", [{}])[0].get("text")
                              or "")
                    if answer:
                        logger.info("Successfully parsed answer from candidates")
                        return answer

                # 2) Try top-level 'output' or 'result' fields (example shape variations)
                for key in ("output", "result", "text", "generated_text"):
                    v = json_res.get(key)
                    if isinstance(v, str) and v:
                        logger.info("Successfully parsed answer from key=%s", key)
                        return v

                # 3) As a last resort, return the pretty JSON
                pretty = json.dumps(json_res, ensure_ascii=False, indent=2)
                logger.info("Returning full JSON response as fallback")
                return pretty

        except requests.RequestException as e:
            last_exc = e
            logger.warning("Network/request error on attempt %d: %s", attempt, e)
        except RuntimeError:
            # Re-raise RuntimeErrors (like 4xx non-retryable) immediately
            raise

        # Backoff before retrying
        if attempt <= RETRIES:
            sleep_time = BACKOFF_SECONDS * attempt
            logger.debug("Sleeping %.2f seconds before retry", sleep_time)
            sleep(sleep_time)

    # If we get here, all retries failed
    raise RuntimeError(f"Request failed after {RETRIES + 1} attempts") from last_exc


if __name__ == "__main__":
    # Simple CLI to test
    prompt = """
Hello! Please write a short welcome message.
"""
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])

    try:
        logger.info("Starting AI request")
        answer = ask_ai(prompt)
        print("\n=== AI ANSWER ===\n")
        print(answer)
        print("\n=================\n")
    except Exception as e:
        logger.error("Error: %s", e)
        sys.exit(1)
