"""Read-only census for the consistency sweep (2026-10-16). Prints only, writes nothing.

Every top-level name defined in tests/browser/*.py and every top-level const or function in tests/**/*.js (HEAD),
with how many times the name appears as a word in the test side outside its own definition. A name that appears
nowhere else (and only once in its own file) is printed UNUSED.
Run from the project root: python -I <this file>
"""
import ast
import re
import subprocess


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout.decode("utf-8")


names = [n for n in git("ls-files", "tests").splitlines() if n.endswith((".py", ".js"))]
texts = {n: git("show", f"HEAD:{n}") for n in names}
JS_TOP = re.compile(r"^(?:export\s+)?(?:const|let|function|async function)\s+([A-Za-z_$][\w$]*)", re.M)
for name, text in sorted(texts.items()):
    if name.endswith(".py"):
        tree = ast.parse(text)
        defined = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                defined.append(node.name)
            elif isinstance(node, ast.Assign):
                defined += [t.id for t in node.targets if isinstance(t, ast.Name)]
    else:
        defined = JS_TOP.findall(text)
    for symbol in defined:
        if symbol.startswith("test_") or symbol.startswith("pytest_") or symbol == "main":
            continue
        word = re.compile(rf"(?<![\w$]){re.escape(symbol)}(?![\w$])")
        own = len(word.findall(text))
        others = sum(len(word.findall(body)) for other, body in texts.items() if other != name)
        if own <= 1 and others == 0:
            print(f"UNUSED {name}:{symbol}")
print(f"scanned {len(names)} test files")
