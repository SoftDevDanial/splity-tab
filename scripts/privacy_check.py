"""Privacy check. A gate that stops private machine details and personal notes from being committed.

HOW TO USE (from anywhere inside the repository)
    python -B scripts/privacy_check.py --staged          # the staged files (pre-commit hook, before every commit)
    python -B scripts/privacy_check.py --message FILE    # a commit message (commit-msg hook), privacy and style
    python -B scripts/privacy_check.py --all             # every tracked file
    python -B scripts/privacy_check.py --history         # every file version, message and tag in every ref

    Exit 0 = clean. Exit 2 = do not commit. Each hit prints the place and the kind of item, never the private value.

WHAT IT CATCHES
    - this computer's name, the user name in a path, the home folder and the folders above the project
      (read at run time, so this file holds none of them), and Claude's project folder names built from them
    - any trace of text the owner excluded from the record
    - job-search wording
    The commit author's public email is allowed. A line holding the word privacy-check-allow is skipped, for the
    documents that state these rules.
"""

import argparse
import getpass
import os
import re
import socket
import subprocess
import sys
from pathlib import Path

ALLOW = "privacy-check-allow"
SEP = r"(?:\\\\|\\|/)+"


def git(*args, inp=None):
    return subprocess.run(["git", *args], input=inp, capture_output=True, check=True).stdout


def path_pattern(path):
    """A local path in any spelling, C:\\a\\b, C:/a/b, C:\\\\a\\\\b or /c/a/b, any case."""
    drive, parts = path.drive.rstrip(":"), [p for p in path.parts[1:] if p not in ("\\", "/")]
    head = rf"(?:{re.escape(drive)}:|/{re.escape(drive)}(?=/))"
    return head + "".join(SEP + re.escape(p) for p in parts) + r"(?![\w-])"


def private_patterns(root):
    found = []
    names = {socket.gethostname(), os.environ.get("COMPUTERNAME", "")}
    for host in sorted(n for n in names if len(n) > 2):
        found.append(("computer name", rf"(?<![\w.]){re.escape(host)}(?![\w@-])"))
    users = {getpass.getuser(), Path.home().name}
    for user in sorted(u for u in users if len(u) > 2):
        found.append(("user name in a path", rf"(?:[\\/]|pytest-of-){re.escape(user)}(?![\w-])"))
    places = [Path.home()] + [p for p in root.parents if len(p.parts) > 1]
    for place in places:
        found.append(("local folder path", path_pattern(place)))
        slug = re.sub(r"[:\\/]", "-", str(place))
        found.append(("Claude project folder name", rf"\b{re.escape(slug)}"))
    return [(k, re.compile(v, re.I)) for k, v in found]


WORDING = [
    ("excluded text trace", re.compile(r"exclude[ -]record|left out at the owner|passage (?:he|the owner) marked", re.I)),
    ("job-search wording", re.compile(r"\b(?:recruit\w*|interview\w*|employers?\b|hiring\b)", re.I)),
]


def scan_text(text, patterns):
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        if ALLOW in line:
            continue
        for kind, rx in patterns:
            if rx.search(line):
                hits.append((n, kind))
    return hits


STYLE = re.compile(r"^[a-z]+(?:\([^)]+\))?: \S")


def message_style(text):
    lines = [l for l in text.splitlines() if not l.startswith("#")]
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return ["empty message"]
    subject, body = lines[0], [l for l in lines[2:] if l.strip()]
    bad = []
    if subject.startswith(("Merge ", "Revert ")):
        return bad
    if len(subject) > 72:
        bad.append(f"subject is {len(subject)} characters, the limit is 72")
    if not STYLE.match(subject):
        bad.append("subject must read type(scope): what changed")
    if subject.endswith("."):
        bad.append("subject ends with a full stop")
    if len(lines) > 1 and lines[1].strip():
        bad.append("line 2 must be blank")
    if len(body) > 4:
        bad.append(f"body has {len(body)} lines, the limit is 3 plus one Refs line")
    if any(len(l) > 72 for l in body):
        bad.append("a body line is over 72 characters")
    if any(l.startswith("Refs:") for l in body[:-1]):
        bad.append("the Refs line must be last")
    return bad


def controls(patterns):
    planted = f"log written to {Path.home() / 'notes' / 'x.txt'}"
    pos = bool(scan_text(planted, patterns))
    neg = scan_text("Write paths relative to the project. Never name the computer.", patterns)
    print(f"CONTROL positive (a planted home path is caught): {pos}")
    print(f"CONTROL negative (false hits on prose about the rule): {len(neg)}")
    return pos and not neg


def main():
    ap = argparse.ArgumentParser(description="privacy check (exit 0 clean, exit 2 stop)")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--staged", action="store_true")
    mode.add_argument("--all", action="store_true")
    mode.add_argument("--history", action="store_true")
    mode.add_argument("--message")
    args = ap.parse_args()

    root = Path(git("rev-parse", "--show-toplevel").decode().strip())
    os.chdir(root)
    patterns = private_patterns(root) + WORDING
    me = Path(__file__).resolve().relative_to(root).as_posix()
    if not controls(patterns):
        print("THE CHECK IS BROKEN. A check whose controls fail proves nothing.")
        return 2

    hits = []
    if args.message:
        text = Path(args.message).read_text(encoding="utf-8", errors="replace")
        hits += [(f"message line {n}", k) for n, k in scan_text(text, patterns)]
        hits += [("message", s) for s in message_style(text)]
    else:
        if args.history:
            objs = git("rev-list", "--objects", "--all").decode("utf-8", "replace").splitlines()
            items = [(o.partition(" ")[2] or o[:7], o.partition(" ")[0]) for o in objs]
        else:
            names = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z") if args.staged else git("ls-files", "-z")
            items = [(n, f":{n}") for n in names.decode("utf-8", "replace").split("\0") if n]
        cat = subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        for name, ref in items:
            cat.stdin.write(ref.encode() + b"\n")
            cat.stdin.flush()
            header = cat.stdout.readline().split()
            if len(header) < 3:
                continue
            data = cat.stdout.read(int(header[2]))
            cat.stdout.read(1)
            if name == me or b"\0" in data[:8000]:
                continue
            text = data.decode("utf-8", "replace")
            if args.history and text.startswith("tree ") and "\ncommitter " in text:
                text = text.partition("\n\n")[2]
            hits += [(f"{name}:{n}", k) for n, k in scan_text(text, patterns)]
        print(f"checked {len(items)} {'objects' if args.history else 'files'}")

    if not hits:
        print("CLEAN. Nothing private found.")
        return 0
    print(f"*** {len(hits)} PRIVACY OR STYLE HIT(S). DO NOT COMMIT ***")
    for where, kind in hits[:200]:
        print(f"  {where}  {kind}")
    print("Use project-relative paths or a placeholder ({home}, {temp}, {workspace}, {host}), and see the")
    print("constitution, Nothing private in committed files, and Commit messages a person can read.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
