"""Read-only checks for the code review (regression --full, 2026-10-16). Prints only, writes nothing.

1. Every tracked file under src/ and tests/ (text files) is scanned for a literal code point of the name class
   (Cc other than TAB, LF, CR, plus U+2028, U+2029 and the 12 Bidi_Control) or of Cf (format characters).
2. The str constants of tests/browser/seeds.py and tests/browser/test_app.py at 62cf3c5~1 and at 62cf3c5 are compared.
Run from the project root: python -I <this file>
"""
import ast
import subprocess
import unicodedata

BIDI = {0x061C, 0x200E, 0x200F, *range(0x202A, 0x202F), *range(0x2066, 0x206A)}


def flagged(cp):
    if cp in (0x09, 0x0A, 0x0D):
        return None
    if cp < 0x20 or 0x7F <= cp < 0xA0:
        return "Cc"
    if cp in (0x2028, 0x2029):
        return "Zl/Zp"
    if cp in BIDI:
        return "Bidi_Control"
    if unicodedata.category(chr(cp)) == "Cf":
        return "Cf"
    return None


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout


files = [name for name in git("ls-files", "src", "tests").decode("utf-8").splitlines()]
scanned, hits = 0, 0
for name in files:
    data = git("show", f"HEAD:{name}")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        continue
    scanned += 1
    for number, line in enumerate(text.split("\n"), 1):
        for column, char in enumerate(line, 1):
            kind = flagged(ord(char))
            if kind:
                hits += 1
                print(f"LITERAL {name} line {number} col {column} U+{ord(char):04X} {kind}")
print(f"scan: {scanned} text files under src/ and tests/ at HEAD, {hits} literal characters of the class or of Cf")


def constants(source):
    return [node.value for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Constant) and isinstance(node.value, str)]


for name in ("tests/browser/seeds.py", "tests/browser/test_app.py"):
    before = constants(git("show", f"62cf3c5~1:{name}").decode("utf-8"))
    after = constants(git("show", f"62cf3c5:{name}").decode("utf-8"))
    print(f"{name}: {len(before)} str constants before, {len(after)} after, equal {before == after}")
    control = constants(git("show", f"4a19b4d~1:{name}").decode("utf-8"))
    print(f"{name}: control against 4a19b4d~1 reports a difference {control != after}")
