#!/usr/bin/env python3
"""Add notes to Anki via AnkiConnect (localhost:8765). Stdlib only, py3.9+.

Used by the /learn skill to push flashcards directly into Anki.
Decks are created on demand (hierarchy via ::, e.g. Learn::Cardiologia).

Usage:
  anki_add.py ping [--launch]
  anki_add.py add --json notes.json [--launch]

JSON shape:
  {
    "deck": "Learn::Cardiologia",
    "notes": [
      {"type": "Basic", "front": "...", "back": "...", "tags": ["learn", "learn::ic"]},
      {"type": "Cloze", "text": "... {{c1::...}} ...", "extra": "...", "tags": ["learn"]}
    ]
  }

Exit 0: connected and processed (duplicates count as skipped, not failure).
Exit 1: could not reach AnkiConnect or the API errored.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

URL = "http://localhost:8765"


def call(action, **params):
    payload = {"action": action, "version": 6, "params": params}
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if body.get("error"):
        raise RuntimeError("AnkiConnect error on %s: %s" % (action, body["error"]))
    return body.get("result")


def connect(launch: bool) -> None:
    try:
        call("version")
        return
    except (urllib.error.URLError, OSError):
        if not launch:
            sys.exit("anki_add: AnkiConnect unreachable (is Anki open?)")
    subprocess.run(["open", "-a", "Anki"], check=False)
    for _ in range(20):
        time.sleep(2)
        try:
            call("version")
            return
        except (urllib.error.URLError, OSError):
            pass
    sys.exit("anki_add: launched Anki but AnkiConnect did not answer in 40s")


def note_payload(deck, note):
    kind = note["type"]
    cloze = "cloze" in kind.lower() or "omiss" in kind.lower()
    if cloze:
        fields = {"Text": note["text"], "Back Extra": note.get("extra", "")}
    else:
        fields = {"Front": note["front"], "Back": note["back"]}
    payload = {
        "deckName": deck,
        "modelName": kind,
        "fields": fields,
        "tags": note.get("tags", []),
        "options": {"allowDuplicate": False, "duplicateScope": "deck"},
    }
    img = note.get("image")
    if img:
        # AnkiConnect copies the file into the media collection and injects
        # <img> into the listed fields. PNG preferred (mobile-safe).
        payload["picture"] = [{
            "path": img["path"],
            "filename": img.get("filename") or os.path.basename(img["path"]),
            "fields": img.get("fields") or (["Back Extra"] if cloze else ["Back"]),
        }]
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Push notes into Anki via AnkiConnect.")
    parser.add_argument("command", choices=["ping", "add"])
    parser.add_argument("--json", dest="json_file", help="notes JSON file (for add)")
    parser.add_argument("--launch", action="store_true", help="open Anki if not running")
    args = parser.parse_args()

    connect(args.launch)
    if args.command == "ping":
        print("ok")
        return

    if not args.json_file:
        sys.exit("anki_add: add requires --json <file>")
    with open(args.json_file, encoding="utf-8") as fh:
        data = json.load(fh)

    deck = data["deck"]
    call("createDeck", deck=deck)  # idempotent, creates Learn:: hierarchy
    payloads = [note_payload(deck, n) for n in data["notes"]]
    # Current AnkiConnect rejects the whole addNotes batch on any duplicate,
    # so pre-filter: duplicates are a skip, never a failure.
    addable = call("canAddNotes", notes=payloads)
    to_add = [p for p, ok in zip(payloads, addable) if ok]
    added = 0
    if to_add:
        try:
            results = call("addNotes", notes=to_add)
        except RuntimeError as exc:
            sys.exit("anki_add: %s" % exc)
        added = sum(1 for r in results if r)
    skipped = len(payloads) - added
    print("deck=%s added=%d skipped=%d" % (deck, added, skipped))


if __name__ == "__main__":
    main()
