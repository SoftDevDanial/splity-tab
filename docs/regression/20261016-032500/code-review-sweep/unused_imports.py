"""Read-only check for the consistency sweep (2026-10-16). Prints only, writes nothing.

For every tracked .py file under tests/ (HEAD), an imported name that the file never reads again is printed UNUSED.
For every tracked .js file under src/ and tests/, a name in an import { ... } list that the file never names again
is printed UNUSED.
Run from the project root: python -I <this file>
"""
import ast
import re
import subprocess


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout.decode("utf-8")


for name in git("ls-files", "tests", "src").splitlines():
    text = git("show", f"HEAD:{name}")
    if name.endswith(".py"):
        tree = ast.parse(text)
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported += [(alias.asname or alias.name).split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imported += [alias.asname or alias.name for alias in node.names]
        used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
            n.value.id for n in ast.walk(tree) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)}
        for symbol in imported:
            if symbol not in used:
                print(f"UNUSED {name}: {symbol}")
    elif name.endswith((".js", ".mjs")):
        for block in re.findall(r"import\s*\{([^}]*)\}\s*from", text):
            for part in block.split(","):
                symbol = part.strip().split(" as ")[-1].strip()
                if symbol and len(re.findall(rf"(?<![\w$]){re.escape(symbol)}(?![\w$])", text)) < 2:
                    print(f"UNUSED {name}: {symbol}")
        for symbol in re.findall(r"import\s+([A-Za-z_$][\w$]*)\s+from", text):
            if len(re.findall(rf"(?<![\w$]){re.escape(symbol)}(?![\w$])", text)) < 2:
                print(f"UNUSED {name}: {symbol}")
print("done")
