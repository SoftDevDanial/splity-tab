"""Runs one command from a folder, with a time limit, and keeps everything it printed in a file next to this script.

The orders forbid shell redirection, so this is how a pytest or node run keeps its full output as evidence. It adds nothing to the
run: the command, its folder, its exit status and its duration go in a header line, and the output follows unchanged.

Usage: python run_logged.py <output file name> <cwd> [--timeout SECONDS] -- <command ...>
Prints the header, the last 6 lines of the output and the path of the file. Its exit status is the command's.
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # node's reporter prints symbols the Windows code page cannot show
    args = sys.argv[1:]
    if "--" not in args:
        sys.exit(__doc__)
    split = args.index("--")
    head, command = args[:split], args[split + 1:]
    name, cwd = head[0], Path(head[1])
    timeout = int(head[head.index("--timeout") + 1]) if "--timeout" in head else 1200
    started = time.time()
    try:
        done = subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        output, status = done.stdout + done.stderr, done.returncode
    except subprocess.TimeoutExpired as expired:
        output, status = f"gave up after {timeout} s\n{expired.stdout or ''}", 124
    header = f"$ {' '.join(command)}   (cwd {cwd})   exit {status}   {time.time() - started:.1f} s wall\n"
    (HERE / name).write_text(header + output, encoding="utf-8")
    print(header.rstrip())
    for line in output.rstrip().splitlines()[-6:]:
        print("  " + line[:240])
    print(f"-> {HERE / name}")
    sys.exit(status)


main()
