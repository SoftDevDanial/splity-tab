"""Read-only scan. Prints every literal code point of the R35 class, and every Cf character, found in the given
source files, with file, line and column. Writes nothing. Run with the project root as the working directory."""
import sys
import unicodedata

CLASS = set([*range(0x00, 0x20), *range(0x7F, 0xA0), 0x2028, 0x2029, 0x061C, 0x200E, 0x200F,
             *range(0x202A, 0x202F), *range(0x2066, 0x206A)])
ALLOWED = {0x09, 0x0A, 0x0D}

for path in sys.argv[1:]:
    with open(path, encoding="utf-8", newline="") as handle:
        text = handle.read()
    for number, line in enumerate(text.split("\n"), start=1):
        for column, char in enumerate(line, start=1):
            cp = ord(char)
            if (cp in CLASS and cp not in ALLOWED) or (cp >= 0x80 and unicodedata.category(char) in ("Cf", "Zs", "Zl", "Zp")):
                kind = "CLASS" if cp in CLASS else unicodedata.category(char)
                print(f"{path}:{number}:{column} U+{cp:04X} {kind} {unicodedata.name(char, '?')}")
