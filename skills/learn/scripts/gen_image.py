#!/usr/bin/env python3
"""Generate an image via OpenAI's Images API (GPT Image). Stdlib only, py3.9+.

Used by the viz-maker agent for organic/anatomical illustrations in /learn.
Exits non-zero with a stderr message on any failure so callers can fall back.
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.openai.com/v1/images/generations"


def load_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key
    sys.exit("gen_image: OPENAI_API_KEY is not set")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an image via OpenAI GPT Image.")
    parser.add_argument("--prompt", required=True, help="image description")
    parser.add_argument("--out", required=True, help="output PNG path")
    parser.add_argument("--size", default="1024x1024", help="e.g. 1024x1024, 1536x1024")
    parser.add_argument("--model", default="gpt-image-2", help="images model name")
    parser.add_argument("--quality", default="medium", choices=["low", "medium", "high"])
    args = parser.parse_args()

    payload = json.dumps({
        "model": args.model,
        "prompt": args.prompt,
        "size": args.size,
        "quality": args.quality,
        "n": 1,
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": "Bearer %s" % load_key(),
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        sys.exit("gen_image: HTTP %s from OpenAI: %s" % (exc.code, detail))
    except (urllib.error.URLError, TimeoutError) as exc:
        sys.exit("gen_image: request failed: %s" % exc)

    try:
        b64 = body["data"][0]["b64_json"]
    except (KeyError, IndexError, TypeError):
        sys.exit("gen_image: unexpected response shape: %s" % json.dumps(body)[:500])

    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(b64))
    print(out)


if __name__ == "__main__":
    main()
