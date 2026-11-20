#!/usr/bin/env python3
"""ai-phrase-checker: fail a draft that uses words, phrases or patterns AI writing overuses.

Usage:
  python3 check.py draft.txt          check a file
  cat draft.txt | python3 check.py    check stdin
  python3 check.py draft.txt --skip comment_cliches --allow landscape
  python3 check.py draft.txt --list my-words.txt

Exit code 0 = PASS, 1 = FAIL (rewrite needed), 2 = bad input.
No third-party packages. Python 3.8+.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EMOJI = "[\U0001F300-\U0001FAFF☀-➿]"
PUNCT = [("—", "em dash"), ("–", "en dash"), (" - ", "spaced hyphen used as a pause"), ("…", "ellipsis character")]


def load_lists(path, skip):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    phrases, structures = [], []
    for key, val in data.items():
        if key.startswith("_") or key in skip:
            continue
        if key == "structures":
            structures = [(s["name"], re.compile(s["regex"], re.I | re.M)) for s in val]
        else:
            phrases += [(p.lower().replace("’", "'"), key) for p in val]
    return phrases, structures


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def check(text, phrases, structures, allow, repeat_limit, max_emoji):
    low = text.lower().replace("’", "'")
    hits = []
    seen = set()
    covered = []  # spans already flagged, so "dive into" is not reported again inside "deep dive into"
    for phrase, group in sorted(phrases, key=lambda p: len(p[0]), reverse=True):
        if phrase in allow or phrase in seen:
            continue
        for m in re.finditer(r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", low):
            if any(m.start() < b and a < m.end() for a, b in covered):
                continue
            seen.add(phrase)
            covered.append(m.span())
            hits.append((line_of(text, m.start()), f"{group}: '{phrase}'"))
            break
    for name, rx in structures:
        m = rx.search(low)
        if m:
            start = m.start() + len(m.group(0)) - len(m.group(0).lstrip(".! \t\n"))
            hits.append((line_of(text, start), f"structure: {name}"))
    for ch, name in PUNCT:
        i = text.find(ch)
        if i >= 0:
            hits.append((line_of(text, i), f"punctuation: {name}"))
    if re.match(r"^\s*" + EMOJI, text):
        hits.append((1, "starts with an emoji"))
    emojis = re.findall(EMOJI, text)
    if len(emojis) > max_emoji:
        hits.append((0, f"{len(emojis)} emoji (limit {max_emoji})"))
    hashtags = re.findall(r"(?<!\w)#\w+", text)
    if len(hashtags) >= 5:
        hits.append((0, f"{len(hashtags)} hashtags"))
    if repeat_limit:
        counts = {}
        for w in re.findall(r"[a-z']{5,}", low):
            counts[w] = counts.get(w, 0) + 1
        for w, c in sorted(counts.items()):
            if c >= repeat_limit and w not in allow:
                hits.append((0, f"word used {c}x: '{w}'"))
    return sorted(hits)


def main():
    ap = argparse.ArgumentParser(description="Flag AI-sounding words, phrases and patterns in a draft.")
    ap.add_argument("file", nargs="?", default="-", help="text file to check, or - for stdin (default)")
    ap.add_argument("--phrases", default=str(HERE / "phrases.json"), help="phrase list JSON (default: phrases.json next to this script)")
    ap.add_argument("--list", action="append", default=[], help="extra plain-text file, one phrase per line (repeatable)")
    ap.add_argument("--skip", action="append", default=[], help="skip a list from the JSON, e.g. comment_cliches or outreach (repeatable)")
    ap.add_argument("--allow", action="append", default=[], help="phrase to let through (repeatable)")
    ap.add_argument("--repeat", type=int, default=3, help="flag any 5+ letter word used this many times; 0 turns it off (default 3)")
    ap.add_argument("--max-emoji", type=int, default=1, help="most emoji allowed (default 1)")
    args = ap.parse_args()

    try:
        text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
        phrases, structures = load_lists(args.phrases, set(args.skip))
        for extra in args.list:
            for line in Path(extra).read_text(encoding="utf-8").splitlines():
                line = line.strip().lower()
                if line and not line.startswith("#"):
                    phrases.append((line, Path(extra).stem))
    except (OSError, ValueError, KeyError, re.error) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)

    allow = {a.lower() for a in args.allow}
    hits = check(text, phrases, structures, allow, args.repeat, args.max_emoji)
    words = len(re.findall(r"\b\w+\b", text))
    if hits:
        print(f"FAIL: {len(hits)} issue(s) in {words} words")
        for line, msg in hits:
            print(f"  line {line}: {msg}" if line else f"  {msg}")
        sys.exit(1)
    print(f"PASS: {words} words, nothing flagged")


if __name__ == "__main__":
    main()
