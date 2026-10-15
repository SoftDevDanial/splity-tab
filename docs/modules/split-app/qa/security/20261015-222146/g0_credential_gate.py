"""G0. The credential gate over the whole tree, run in the foreground from the project root, its output kept on disk.

python -B docs/modules/split-app/qa/security/20261015-222146/g0_credential_gate.py
Runs the sdlc plugin's credential_sweep.py with the project root as its working directory, waits for it (bounded at
300 s), and writes its exit code and its full stdout and stderr to credential-gate.txt beside this file. The gate prints
paths and key names only, never a value (constitution, "Secrets never sit in the working tree").
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
GATE = "{sdlc}/harness/credential_sweep.py"

started = time.strftime("%Y-%m-%dT%H:%M:%S")
done = subprocess.run([sys.executable, "-B", GATE], cwd=ROOT, capture_output=True, text=True, timeout=300)
text = (f"command: python -B {GATE}\ncwd: {ROOT}\nstarted: {started}\nended: {time.strftime('%Y-%m-%dT%H:%M:%S')}\n"
        f"exit code: {done.returncode}\n--- stdout ---\n{done.stdout}--- stderr ---\n{done.stderr}")
(HERE / "credential-gate.txt").write_text(text, encoding="utf-8")
print(text)
sys.exit(done.returncode)
