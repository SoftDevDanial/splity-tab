"""Read-only census for the consistency sweep (2026-10-16). Prints only, writes nothing.

For every name exported by a file under src/ (HEAD), lists which other files under src/ and tests/ name it as a
word, split into src importers and test users. A name no other src file uses is printed as SRC-UNUSED.
Run from the project root: python -I <this file>
"""
import re
import subprocess


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout.decode("utf-8")


files = {name: git("show", f"HEAD:{name}") for name in git("ls-files", "src", "tests").splitlines()
         if name.endswith((".js", ".py", ".html", ".mjs"))}
files["index.html"] = git("show", "HEAD:index.html")
EXPORT = re.compile(r"^export\s+(?:async\s+)?(?:function|const|let|class)\s+([A-Za-z_$][\w$]*)", re.M)
for name, text in sorted(files.items()):
    if not name.startswith("src/"):
        continue
    for symbol in EXPORT.findall(text):
        word = re.compile(rf"(?<![\w$]){re.escape(symbol)}(?![\w$])")
        src_users = [other for other, body in files.items() if other != name and other.startswith(("src/", "index"))
                     and word.search(body)]
        test_users = [other for other, body in files.items() if other.startswith("tests/") and word.search(body)]
        own = len(word.findall(text))
        flag = "SRC-UNUSED" if not src_users else "ok"
        print(f"{flag:10} {name}:{symbol} own-uses {own} src {len(src_users)} tests {len(test_users)}"
              + (f" tests-in {','.join(t.split('/')[-1] for t in test_users)}" if not src_users else ""))
