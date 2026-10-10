"""Regression QA, step 5: the scenario table and the findings file, built from the run outputs in this folder.

Every covering test is looked up in the saved output before it is counted:
  node tests    -> node-test.txt (a line "✔ <title> (<ms>)" must exist)
  pytest tests  -> pytest-collect.txt (the id must be collected) and junit.xml (no failure, error or skip child)
  driven checks -> driven-checks.json, driven-r34.json, flows.json, gates-summary.json (the checks cited all PASS)
A citation that cannot be found stops the script with an error, so no row can claim a test that did not run.
Writes scenario-table.json and scenario-table.md here, and the findings file at
docs/modules/split-app/findings/regression-qa.md (the one report the orchestrator asked for).
"""
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

EVID = Path(__file__).resolve().parent
ROOT = Path(r"{workspace}\examples\split")
FINDINGS = ROOT / "docs" / "modules" / "split-app" / "findings" / "regression-qa.md"
TA = "tests/browser/test_app.py"


def jt(text):
    """The JavaScript JSON.stringify of a string, as the node test titles print it."""
    return json.dumps(text, ensure_ascii=False)


# ------------------------------------------------------------------ the saved outputs
NODE_TEXT = (EVID / "node-test.txt").read_text(encoding="utf-8")
NODE_PASSED = set()
for line in NODE_TEXT.splitlines():
    match = re.match(r"^✔ (.*) \(([\d.]+)ms\)$", line)
    if match:
        NODE_PASSED.add(match.group(1))
NODE_COUNTS = {key: int(re.search(rf"^ℹ {key} (\d+)", NODE_TEXT, re.M).group(1))
               for key in ("tests", "pass", "fail", "skipped", "todo")}
NODE_DURATION = float(re.search(r"^ℹ duration_ms ([\d.]+)", NODE_TEXT, re.M).group(1))

COLLECT = [line.split("::", 1)[1].strip() for line in (EVID / "pytest-collect.txt").read_text(encoding="utf-8").splitlines()
           if "::" in line]
COLLECT_SET = set(COLLECT)
JUNIT = {}
for case in ET.parse(EVID / "junit.xml").getroot().iter("testcase"):
    bad = [child.tag for child in case if child.tag in ("failure", "error", "skipped")]
    JUNIT[case.get("name")] = "passed" if not bad else "+".join(bad)
SUITES = json.loads((EVID / "suites-summary.json").read_text(encoding="utf-8"))


def load(name):
    return json.loads((EVID / name).read_text(encoding="utf-8"))


DRIVEN_FILES = {"driven_checks.py": load("driven-checks.json"), "driven_r34.py": load("driven-r34.json"),
                "flows.py": load("flows.json")}
DRIVEN = {}
DRIVEN_OWNER = {}
for owner, data in DRIVEN_FILES.items():
    for check in data["checks"]:
        DRIVEN.setdefault(check["group"], []).append(check)
        DRIVEN_OWNER[check["group"]] = owner
GATES = load("gates-summary.json")


# ------------------------------------------------------------------ references, checked against the outputs
def N(file, title):
    return ("node", file, title)


def P(name):
    return ("py", TA, name)


def G(pattern, count):
    return ("pyglob", TA, pattern, count)


def D(group, rows=None):
    """A driven group, or only the checks whose step starts with `rows` (for example "row b:")."""
    return ("drv", group, rows)


def GATE(name):
    return ("gate", name)


def glob_regex(pattern):
    return re.compile(re.escape(pattern).replace(r"\*", ".*"))


def check_ref(ref):
    kind = ref[0]
    if kind == "node":
        if ref[2] not in NODE_PASSED:
            raise SystemExit(f"NOT FOUND, or not passed, in node-test.txt: {ref[2]}")
        return f"{ref[1]} :: {ref[2]}"
    if kind == "py":
        if ref[2] not in COLLECT_SET:
            raise SystemExit(f"NOT COLLECTED: {ref[2]}")
        if JUNIT.get(ref[2]) != "passed":
            raise SystemExit(f"NOT PASSED in junit.xml: {ref[2]} = {JUNIT.get(ref[2])}")
        return f"{ref[1]} :: {ref[2]}"
    if kind == "pyglob":
        regex = glob_regex(ref[2])
        found = [name for name in COLLECT if regex.fullmatch(name)]
        if len(found) != ref[3]:
            raise SystemExit(f"GLOB COUNT {len(found)} != {ref[3]}: {ref[2]}")
        bad = [name for name in found if JUNIT.get(name) != "passed"]
        if bad:
            raise SystemExit(f"NOT PASSED in junit.xml: {bad[:3]}")
        return f"{ref[1]} :: {ref[2]} ({ref[3]} ids)"
    if kind == "drv":
        group, rows = ref[1], ref[2]
        if group not in DRIVEN:
            raise SystemExit(f"NO DRIVEN GROUP: {group}")
        checks = [c for c in DRIVEN[group] if rows is None or c["step"].startswith(rows) or c["group"] == group and rows is None]
        if rows is not None:
            checks = [c for c in DRIVEN[group] if c["step"].startswith(rows)]
        if not checks:
            raise SystemExit(f"NO CHECKS for {group} {rows}")
        if any(c["result"] != "PASS" for c in checks):
            raise SystemExit(f"DRIVEN CHECK NOT PASS: {group} {rows}")
        scope = f", rows starting '{rows}'" if rows else ""
        return f"{DRIVEN_OWNER[group]} (driven), group '{group}'{scope}, {len(checks)} checks"
    if kind == "gate":
        if ref[1] == "fidelity":
            pairs = GATES["fidelity_pairs"]
            if not all(p and p["dimensions_match"] is True and p["mismatch_pixels"] == 0 for p in pairs.values()):
                raise SystemExit("FIDELITY PAIRS NOT ALL PASS")
            return f"run_gates.py (driven), tests/browser/fidelity/run.py, {len(pairs)} pairs, pixel gate"
        if ref[1] == "live":
            summary = GATES["live_summary"]
            if summary is None or summary["result"] != "PASS" or summary["steps"] != 7:
                raise SystemExit("LIVE GATE NOT PASS")
            return "run_gates.py (driven), tests/browser/live_e2e.py, 7 steps"
    raise SystemExit(f"BAD REF {ref}")


# ------------------------------------------------------------------ the scenario items
ROWS = []


def add(doc, r, scenario, row, refs, note="", untested=None):
    ROWS.append({"doc": doc, "r": r, "scenario": scenario, "row": row, "refs": refs, "note": note, "untested": untested})


CORE = "split-core"
MONEY, ALLOC, BILL, RESULT, INV, SUMM, HYG = (
    "money.test.js", "allocate.test.js", "bill.test.js", "result.test.js", "invariants.test.js",
    "summary.test.js", "hygiene.test.js")

# --- split-core: 33 plain scenarios and 146 outline rows (21 outlines)
for text, cents in [("12", 1200), ("12.5", 1250), ("12.50", 1250), ("0.01", 1), ("99999.99", 9999999), ("1.15", 115),
                    ("4.35", 435), ("0.29", 29), (" 12.50 ", 1250), ("007", 700), ("12.", 1200), ("0000000012.50", 1250)]:
    add(CORE, "R1", "parseAmount accepts valid amounts as exact cents", f"{jt(text)} is {cents}",
        [N(MONEY, f"@R1 parseAmount({jt(text)}) is {cents} cents")])
for text in ["0", "0.00", "100000", "99999.991", "12.505", "13.505", "-5", "+5", "1,000", ".5", "1e3", "0x10",
             "Infinity", "NaN", "abc", "12 50", "１２"]:
    add(CORE, "R1 R2", "parseAmount rejects invalid text as invalid, not empty", jt(text),
        [N(MONEY, f"@R1 @R2 parseAmount({jt(text)}) is invalid, not empty")])
add(CORE, "R1 R2", "A 401-character amount is rejected without overflow or exception", "",
    [N(MONEY, "@R1 @R2 a 401-character amount is invalid and does not throw")])
add(CORE, "R1 R3", "A whole part longer than the ceiling's is refused before any numeric conversion", "",
    [N(MONEY, "@R1 @R3 a whole part longer than the ceiling's is refused before any numeric conversion")],
    note="the test spies on Number, and its positive controls show the spy is not blind")
for text in ['""', '"   "']:
    add(CORE, "R2", "Empty or white-space text is reported as empty", text,
        [N(MONEY, f"@R2 {text} is reported as empty by both parsers")])
add(CORE, "R2", "The parsers never throw for any string", "",
    [N(MONEY, "@R2 the parsers never throw and always return a well-formed result")],
    note="500 seeded strings; the test alphabet has one space where qa.md lists two (see observation 12)")
for text, maximum, bp in [("0", 30, 0), ("10", 30, 1000), ("6", 20, 600), ("6.5", 20, 650), ("6.25", 20, 625),
                          ("30", 30, 3000), ("30.00", 30, 3000), ("20", 20, 2000), ("0.01", 30, 1), ("6.", 20, 600),
                          ("06", 20, 600)]:
    add(CORE, "R3", "parseRate reads basis points within its maximum", f"{jt(text)}, max {maximum} is {bp} bp",
        [N(MONEY, f"@R3 parseRate({jt(text)}, {maximum}) is {bp} bp")])
for text, maximum in [("30.01", 30), ("20.01", 20), ("25", 20), ("-1", 30), ("6.255", 20), ("10%", 30)]:
    add(CORE, "R3", "parseRate reads basis points within its maximum", f"{jt(text)}, max {maximum} is invalid",
        [N(MONEY, f"@R3 parseRate({jt(text)}, {maximum}) is invalid")])
for cents, text in [(0, "RM 0.00"), (1, "RM 0.01"), (10, "RM 0.10"), (100, "RM 1.00"), (3887, "RM 38.87"),
                    (11660, "RM 116.60"), (15599999, "RM 155999.99"), (779999922, "RM 7799999.22")]:
    add(CORE, "R4", "formatMoney writes RM, a space, ringgit and two sen digits", f"{cents} is {jt(text)}",
        [N(MONEY, f"@R4 formatMoney({cents}) is {jt(text)}")])
for bp, text in [(0, "0%"), (600, "6%"), (1000, "10%"), (650, "6.5%"), (625, "6.25%"), (605, "6.05%"), (3000, "30%")]:
    add(CORE, "R5", "formatRate drops trailing zeros and adds a percent sign", f"{bp} is {jt(text)}",
        [N(MONEY, f"@R5 formatRate({bp}) is {jt(text)}")])
for sub, sbp, tbp, total in [(10000, 1000, 600, 11660), (5940, 1000, 600, 6926), (8765, 1000, 600, 10221),
                             (5, 1000, 0, 6), (25, 1000, 0, 28), (4, 1000, 0, 4), (1000, 0, 0, 1000),
                             (5000, 1250, 625, 5977), (9999999, 3000, 2000, 15599999),
                             (499999950, 3000, 2000, 779999922)]:
    add(CORE, "R6", "Service and SST round half up to the cent", f"subtotal {sub}, service {sbp}, SST {tbp}, total {total}",
        [N(RESULT, f"@R6 billCharges({sub}, {sbp}, {tbp}) totals {total}")],
        note="the test checks service, base, SST and total together with both rates")
for amount, count in [(11660, 3), (1800, 2), (1001, 3), (1, 3), (0, 2), (10221, 4), (15599999, 12)]:
    add(CORE, "R7", "allocateEvenly floors and hands leftover sen to the top", f"{amount} over {count}",
        [N(ALLOC, f"@R7 allocateEvenly({amount}, {count})")])
for amount, weights, trap in [(986, [2490, 1350, 2100], ""), (10, [0, 1, 1, 1], ""), (0, [5, 7], ""),
                              (249, [0, 1251, 250], ""), (236419679, [314963010, 157876348], "BigInt trap: "),
                              (61846725, [49676084, 322894546], "BigInt trap: "),
                              (178450942, [111531837, 207130558], "BigInt trap: ")]:
    wtext = ",".join(str(w) for w in weights)
    add(CORE, "R8", "allocateByWeight floors exactly and skips zero weights for leftovers", f"{amount} over [{wtext}]",
        [N(ALLOC, f"@R8 {trap}allocateByWeight({amount}, [{wtext}])")])
add(CORE, "R8 R23", "allocateByWeight gives the MAX-I charges split exactly, with products past 2^53", "",
    [N(ALLOC, "@R8 @R23 allocateByWeight gives the MAX-I charges split exactly, with products past 2^53")])
for title in ["allocateEvenly(10, 0) throws RangeError", "allocateEvenly(10, 1.5) throws RangeError",
              "allocateEvenly(-1, 2) throws RangeError", "allocateEvenly(0.5, 2) throws RangeError",
              "allocateByWeight(10, []) throws RangeError", "allocateByWeight(10, [0, 0]) throws RangeError",
              "allocateByWeight(10, [1, -1]) throws RangeError", "allocateByWeight(10, [1.5, 1]) throws RangeError",
              "allocateByWeight(-1, [1]) throws RangeError"]:
    add(CORE, "R9", "Allocation rejects impossible input", title.replace(" throws RangeError", ""),
        [N(ALLOC, f"@R9 {title}")])
add(CORE, "R10", "A new bill has two people, even mode and the default rates", "",
    [N(BILL, "@R10 a new bill has two people, even mode and the default rates")])
add(CORE, "R11", "Adding a person appends an empty-named person with the next id", "",
    [N(BILL, "@R11 adding a person appends an empty-named person with the next id")])
add(CORE, "R11", "A new person's id never reuses a removed id", "",
    [N(BILL, "@R11 a new person's id comes from nextId, so it never reuses a removed id")])
add(CORE, "R11", "Adding a 13th person does nothing", "",
    [N(BILL, "@R11 the twelfth person is accepted and the thirteenth does nothing")])
add(CORE, "R12", "Removing a person removes them from every item", "",
    [N(BILL, "@R12 removing a person removes them from every item")])
for row in ["a new bill, p1", "the S1 bill, p99"]:
    add(CORE, "R12", "Removing is refused at 2 people or for an unknown id", row,
        [N(BILL, "@R12 removing is refused at 2 people or for an unknown id")],
        note="one test covers both rows")
add(CORE, "R13", "Adding an item appends an empty, unassigned item", "",
    [N(BILL, "@R13 adding an item appends an empty, unassigned item")])
add(CORE, "R13", "The 51st item is refused and removing works at any time", "",
    [N(BILL, "@R13 the 51st item is refused and removing works at any time")])
add(CORE, "R14", "Tapping toggles a person on an item", "",
    [N(BILL, "@R14 tapping toggles a person on an item"), N(BILL, "@R14 an unknown item or person id returns the same bill")])
add(CORE, "R15", "Switching modes keeps both sets of input", "",
    [N(BILL, "@R15 switching modes keeps both sets of input")],
    note="the same test checks that setMode with other returns the same object")
add(CORE, "R15", "Setters store text exactly as typed", "",
    [N(BILL, "@R15 setters store text exactly as typed"), N(BILL, "@R15 each setter changes only its own field")])
add(CORE, "R16", "No action mutates its input", "",
    [N(BILL, "@R16 no action mutates a deep-frozen bill and changes return new objects")])
add(CORE, "R16", "The other functions that take objects leave them alone", "",
    [N(ALLOC, "@R16 allocateByWeight leaves frozen weights alone"),
     N(BILL, "@R16 @R17 the labels leave a frozen person or item alone"),
     N(SUMM, "@R16 summaryText leaves a deep-frozen result alone")])
for kind, name, index, label in [("person", "Aisyah", 0, "Aisyah"), ("person", " Ben ", 1, "Ben"),
                                 ("person", "   ", 2, "Person 3"), ("person", "", 0, "Person 1"),
                                 ("item", "Satay", 3, "Satay"), ("item", "", 0, "Item 1")]:
    add(CORE, "R17", "Display names fall back to their position", f"{kind} {jt(name)} at {index} is {jt(label)}",
        [N(BILL, f"@R17 {kind} named {jt(name)} at index {index} is {jt(label)}")])
for number, reason in enumerate(["rates", "rates", "rates", "subtotal", "subtotal", "subtotal", "no-items", "prices",
                                 "prices"], start=1):
    add(CORE, "R18", "The first blocking rule wins", f"row {number}, {reason}",
        [N(RESULT, f'@R18 blocking row {number} is "{reason}"')])
add(CORE, "R18 R20", "Even mode ignores broken items", "",
    [N(RESULT, "@R18 @R20 even mode ignores broken items")])
add(CORE, "R19", "Unassigned items are counted and the charges are still known", "",
    [N(RESULT, "@R19 unassigned items are counted and the charges are still known")])
add(CORE, "R19", "Two unassigned items give a count of 2", "",
    [N(RESULT, "@R19 two unassigned items give a count of 2")])
for bill in ["S2", "E1", "E2", "E3", "MAX-E"]:
    add(CORE, "R20", "Even results match the worked examples", bill,
        [N(RESULT, f"@R20 @R23 even result for {bill}")])
for bill in ["S1", "I2", "I3", "I4", "MAX-I"]:
    add(CORE, "R21", "By-item results match the worked examples", bill,
        [N(RESULT, f"@R21 @R23 by-item result for {bill}")])
add(CORE, "R21", "A shared item's leftover sen follow the people list, not the tap order", "",
    [N(RESULT, "@R21 a shared item's leftover sen follow the people list, not the tap order")])
add(CORE, "R22", "Generated bills always add up", "",
    [N(INV, "@R22 generated bills always add up")])
add(CORE, "R23", "The largest bills compute exactly", "MAX-E and MAX-I",
    [N(RESULT, "@R20 @R23 even result for MAX-E"), N(RESULT, "@R21 @R23 by-item result for MAX-I"),
     N(RESULT, "@R23 MAX-I charges are exact at the bound")])
for bill, title in [("S2", "summary text for S2 is exact"), ("S1", "summary text for S1 is exact"),
                    ("E2", "summary text for E2 zero rates is exact"), ("E3", "summary text for E3 decimal rates is exact"),
                    ("I2", "summary text for I2 zero share is exact")]:
    add(CORE, "R24", "Summary text is exact", bill, [N(SUMM, f"@R24 {title}")])
add(CORE, "R24", "A blank name prints as its position", "",
    [N(SUMM, "@R24 a blank name prints as its position")])
for label in ["LF", "CR", "VT", "FF", "NEL", "LS", "PS"]:
    add(CORE, "R24", "A line break inside a name prints as a space, so it cannot forge a line", label,
        [N(SUMM, f"@R24 a {label} inside a name prints as a space, so it cannot forge a line")])
for label in ["NUL", "FS", "GS", "RS", "ESC"]:
    add(CORE, "R24", "Any other control character in a name prints as a space", label,
        [N(SUMM, f"@R24 a {label} inside a name prints as a space, so no reader can cut the summary there")])
add(CORE, "R24", "A right-to-left override in a name cannot reorder the share", "",
    [N(SUMM, "@R24 a right-to-left override in a name cannot reorder the share")])
add(CORE, "R24", "Exactly the R24 class prints as a space, every other code point up to U+2069 as typed", "",
    [N(SUMM, "@R24 exactly the R24 class prints as a space, every other code point up to U+2069 as typed")])
add(CORE, "R24", "Every code point above U+2069 prints as typed", "",
    [N(SUMM, "@R24 every code point above U+2069 prints as typed")])
add(CORE, "R24", "Every member of the class in one name is replaced, one space each", "",
    [N(SUMM, "@R24 every member of the class in one name is replaced, one space each")])
add(CORE, "R24", "A lone surrogate prints as typed", "",
    [N(SUMM, "@R24 a lone surrogate is not in the class, so it prints as typed")])
add(CORE, "R24", "By-item rows get the same line-break guard", "",
    [N(SUMM, "@R24 by-item rows get the same line-break guard")])
for kind in ["blocked", "unassigned"]:
    add(CORE, "R24", "summaryText refuses results without shares", f"kind {kind}",
        [N(SUMM, "@R24 results without shares are refused with TypeError")], note="one test covers both rows")
add(CORE, "R25", "The core files are pure", "",
    [N(HYG, "@R25 the scan sees the core files"),
     N(HYG, "@R25 the scanner catches what it should (negative control)"),
     N(HYG, "@R25 the code-only scan reads code, and skips comments, strings, template text and regex bodies"),
     *[N(HYG, f"@R25 {name}.js uses no banned name") for name in ["allocate", "bill", "money", "result", "summary"]],
     *[N(HYG, f"@R25 {name}.js imports only from src/core/") for name in ["allocate", "bill", "money", "result", "summary"]],
     N(HYG, "@R25 the core files do import each other (the import scan is not blind)"),
     N(HYG, "@R25 const run = (text) => eval(text); served into each core file goes red as eval"),
     N(HYG, "@R25 const make = (body) => Function(body); served into each core file goes red as Function"),
     N(HYG, "@R25 const build = (body) => new Function(body); served into each core file goes red as Function"),
     N(HYG, "@R25 const load = (name) => import(name); served into each core file goes red as import("),
     N(HYG, "@R25 const soon = (fn) => queueMicrotask(fn); served into each core file goes red as queueMicrotask"),
     N(HYG, "@R25 const later = (fn) => setImmediate(fn); served into each core file goes red as setImmediate"),
     N(HYG, "@R25 const now = () => performance.now(); served into each core file goes red as performance"),
     N(HYG, "@R25 const pick = () => crypto.getRandomValues(new Uint32Array(1))[0]; served into each core file goes red as crypto"),
     N(HYG, "@R25 const open = (url) => new WebSocket(url); served into each core file goes red as WebSocket"),
     N(HYG, "@R25 const env = () => process.env.SPLIT; served into each core file goes red as process"),
     N(HYG, "@R25 const load = (name) => require(name); served into each core file goes red as require")])
RUNTIME_TRAP = [
    "@R25 runtime trap: the core touches no banned global or method while it loads and while every export runs",
    "@R25 runtime trap: every trap fires for core code and not for test code (negative control)",
    "@R25 runtime trap: the trap lists are exactly the pinned ones, so no trap is dropped unseen",
    "@R25 runtime trap: every name the source scan bans has a trap",
    "@R25 runtime trap: every trap is put back after a run, also after a body that throws",
    "@R25 runtime trap: every run loads its own copy of the core",
    "@R25 runtime trap: a run whose body throws leaves no hits for the next run",
    "@R25 runtime trap: a stack that cannot be read does not leave the recorder stuck",
]
PLANTS = ["F1", "F2", "F3", "F4", "F4b", "F5", "F6", "F6b", "F7", "F8", "F9", "F10"]
add(CORE, "R25", "The core touches no banned global or method at load or while every export runs (runtime trap)", "",
    [N(HYG, t) for t in RUNTIME_TRAP] +
    [N(HYG, f"@R25 runtime trap catches the security re-check's {p} plant in every core file") for p in PLANTS])
add(CORE, "R26", "Equal names are stored as typed", "",
    [N(BILL, "@R26 equal names are stored as typed and nobody is merged")])
add(CORE, "R26", "Tapping and removing address a person by id, not by name", "",
    [N(BILL, "@R26 tapping and removing address a person by id, not by name")])
add(CORE, "R26", "Equal names give one row each", "D1, even", [N(RESULT, "@R26 D1: two people called Ben give two even rows")])
add(CORE, "R26", "Equal names give one row each", "D2, item",
    [N(RESULT, "@R26 D2: two people called Ben give two by-item rows, only the tapped one pays")])
add(CORE, "R26", "Equal names give one summary line each", "D1, even",
    [N(SUMM, "@R24 summary text for D1 equal names, even is exact"), N(SUMM, "@R26 equal names print one line each")])
add(CORE, "R26", "Equal names give one summary line each", "D2, item",
    [N(SUMM, "@R24 summary text for D2 equal names, by item is exact"), N(SUMM, "@R26 equal names print one line each")])

# --- split-app: 53 plain scenarios and 109 outline rows (25 outlines)
APP = "split-app"
add(APP, "R1", "The entry point loads only its own files", "", [P("test_R1_entry_point_loads_only_its_own_files")])
add(APP, "R1", "The page works from a sub-path, as on GitHub Pages", "", [P("test_R1_page_works_from_a_sub_path")])
add(APP, "R2", "Cold boot is a new bill with no seed", "", [P("test_R2_cold_boot_is_a_new_bill_with_no_seed")])
add(APP, "R2", "No sample data ships", "", [P("test_R2_no_sample_data_ships")])
add(APP, "R3", "The rendered markup matches its golden", "S3, cold boot, bill-empty",
    [P("test_R3_rendered_markup_matches_its_golden[S3-None-bill-empty]")])
add(APP, "R3", "The rendered markup matches its golden", "S2 seeded, bill-even",
    [P("test_R3_a_restored_bill_matches_its_golden[S2]"),
     P("test_R3_rendered_markup_matches_its_golden_by_gestures[S2-build_s2-bill-even]")],
    note="the seeded walk is the scenario; the gesture-built walk is the same golden built by hand")
add(APP, "R3", "The rendered markup matches its golden", "S1 seeded, bill-items",
    [P("test_R3_a_restored_bill_matches_its_golden[S1]"),
     P("test_R3_rendered_markup_matches_its_golden_by_gestures[S1-build_s1-bill-items]")])
add(APP, "R3", "The rendered markup matches its golden", "S5 seeded, bill-unassigned",
    [P("test_R3_a_restored_bill_matches_its_golden[S5]"),
     P("test_R3_rendered_markup_matches_its_golden_by_gestures[S5-build_s5-bill-unassigned]")])
add(APP, "R4", "Person rows carry their names and labels", "",
    [P("test_R4_person_rows_carry_their_names_and_labels"), P("test_R3_a_restored_bill_matches_its_golden[S1]")],
    note="names typed by gestures, the same rows; the seeded S1 walk matches bill-items.html")
add(APP, "R4 R5", "A blank name falls back to its position everywhere but the field", "",
    [P("test_R4_a_blank_name_falls_back_to_its_position_but_not_in_the_field"),
     P("test_R5_a_person_label_follows_the_name_into_every_toggle"),
     P("test_R5_a_blank_name_reads_as_its_position_in_the_shares_row")],
    note="toggles and shares row checked on the gesture-built S1 bill")
add(APP, "R5", "Renaming a person updates every place on each keystroke", "",
    [P("test_R5_renaming_a_person_updates_the_remove_name_on_each_keystroke"),
     P("test_R5_a_new_name_reaches_the_copied_text"), D("D1 R5 rename per keystroke, S1 seed")],
    note="the suite checks the remove name on each key and the final toggles; D1 drives the toggles and shares row on each key")
add(APP, "R5", "Renaming an item updates its accessible names", "",
    [P("test_R5_renaming_an_item_updates_its_accessible_names")])
add(APP, "R6", "Add person until the limit", "", [P("test_R6_add_person_until_the_limit")],
    note="the cursor and the specimen properties are compared to the S8 button in states.html")
add(APP, "R7", "Remove a person and they leave every item", "",
    [P("test_R7_removing_a_person_takes_them_off_every_item"), P("test_R7_removing_a_person_can_leave_an_item_without_anyone"),
     P("test_R7_remove_a_person")], note="built by gestures, the same screen as the S1 seed")
for bill, pattern in [("S2, Remove Chen", "test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing[S2-person-3-of-3-*]"),
                      ("S8, Remove Mei Ling", "test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing[S8-person-12-of-12-*]"),
                      ("S1, Remove Satay", "test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing[S1-item-4-of-4-*]"),
                      ("S1 with only its last item, Remove Satay", "test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing[S1-only-item-*]")]:
    add(APP, "R7", "A repeat press on the last Remove removes that row and adds nothing", bill, [G(pattern, 12)],
        note="sizes 360x640, 390x844, 1280x800; gestures single, mouse double, mouse triple, touch double")
for row, pattern in [("S1, Remove Char kuey teow", "test_R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it[item-2-of-4-*]"),
                     ("S2 with five people, Remove P2", "test_R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it[person-2-of-5-*]")]:
    add(APP, "R34", "After a double click or double tap on a middle Remove, focus is where one click puts it", row,
        [G(pattern, 2)], note="mouse double click and touch double tap")
add(APP, "R7", "A press of its own is never held back", "",
    [P("test_R7_a_separate_click_on_what_slid_under_the_pointer_is_not_held_back"),
     P("test_R7_the_guard_of_a_remove_click_ends_at_the_next_press"),
     P("test_R7_after_a_remove_click_a_double_click_on_a_name_still_selects_the_word")])
add(APP, "R6", "A repeat press on Add person adds one person and keeps it", "middle of the button",
    [G("test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it[*-centre]", 36)],
    note="people 2, 3, 4, 5 by sizes and gestures")
add(APP, "R6", "A repeat press on Add person adds one person and keeps it", "22 px in from the right edge",
    [G("test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it[*-right-edge]", 36)],
    note="people 2, 3, 4, 5 by sizes and gestures")
add(APP, "R12", "A repeat press on Add item adds one item and never reaches the page", "middle of the button",
    [G("test_R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page[*-centre]", 18)],
    note="items 1 and 4 by sizes and gestures, with the body recorder")
add(APP, "R12", "A repeat press on Add item adds one item and never reaches the page", "22 px in from the right edge",
    [G("test_R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page[*-right-edge]", 18)],
    note="items 1 and 4 by sizes and gestures, with the body recorder")
add(APP, "R7 R12", "A repeat press on a chip under a pending price error never removes the item", "widths 375 and 390",
    [G("test_R7_a_repeat_press_on_a_chip_under_a_pending_price_error_never_removes_the_item[*]", 6)],
    note="widths 375 and 390 with mouse double, mouse triple and touch double")
add(APP, "R42", "Two people may have the same name", "",
    [P("test_R42_duplicate_names_are_accepted_and_act_on_their_own_row"),
     P("test_R42_duplicate_names_through_the_whole_flow"), P("test_R42_the_draft_keeps_both_people_with_the_same_name")])
add(APP, "R8", "Switching modes keeps both sets of input", "",
    [P("test_R8_switching_modes_keeps_the_subtotal"), P("test_R8_switching_modes_keeps_both_sets_of_input"),
     P("test_R8_the_panel_follows_each_mode"), P("test_R8_both_sets_of_input_survive_a_reload")])
add(APP, "R8", "Arrow keys move between the modes", "", [P("test_R8_arrow_keys_move_between_the_modes")])
add(APP, "R9", "The subtotal field drives the even split", "",
    [P("test_R9_subtotal_field_has_its_unit_label_and_input_mode"), P("test_R9_a_subtotal_drives_the_even_split")])
for field in ["subtotal", "item-price", "service", "sst"]:
    add(APP, "R10", "An inline error waits for the field to be left", field,
        [P(f"test_R10_an_inline_error_waits_for_the_field_to_be_left[{field}]")])
add(APP, "R10", "An empty field never shows an error", "",
    [P("test_R10_an_empty_field_never_shows_an_error"), P("test_R10_an_empty_rate_never_shows_an_error")])
add(APP, "R10", "Typing invalid text in a focused field does not show the error early", "",
    [P("test_R10_typing_bad_text_in_a_focused_field_shows_no_error_early")])
add(APP, "R10", "A restored invalid field shows its error at once", "",
    [P("test_R10_a_restored_bad_field_shows_its_error_at_once")])
add(APP, "R10", "An error survives a mode switch", "", [P("test_R10_an_error_survives_a_mode_switch")])
for field in ["subtotal", "item-price", "service", "sst"]:
    add(APP, "R10 R13", "A press below an invalid field lands on the control it started on", field,
        [P(f"test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[{field}-mouse]"),
         P(f"test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[{field}-touch]")],
        note="a mouse press and a touch tap")
add(APP, "R13", "A tap on a person below an invalid, unflagged price toggles them and then shows the error", "",
    [P("test_R13_a_tap_below_an_invalid_price_toggles_that_person_and_then_shows_the_error[mouse]"),
     P("test_R13_a_tap_below_an_invalid_price_toggles_that_person_and_then_shows_the_error[touch]")])
add(APP, "R10", "The error waits for the release, and only a press holds it back", "",
    [P("test_R10_the_error_waits_for_the_mouse_button_to_come_up"),
     P("test_R10_pressing_empty_space_also_waits_for_the_release"),
     P("test_R10_a_keyboard_blur_shows_the_error_at_once_even_after_a_press[mouse]"),
     P("test_R10_a_keyboard_blur_shows_the_error_at_once_even_after_a_press[touch]"),
     P("test_R10_a_keyboard_blur_shows_the_error_at_once_even_after_a_press[held]")])
add(APP, "R11", "Item rows carry their names and labels", "",
    [P("test_R11_item_rows_carry_their_names_and_labels"), P("test_R3_a_restored_bill_matches_its_golden[S1]")],
    note="names typed by gestures, the same rows; the seeded S1 walk matches bill-items.html")
add(APP, "R12", "Add an item, remove one, and reach the limit", "",
    [P("test_R12_add_an_item_remove_one_and_reach_the_limit")], note="the cursor and the specimen properties are compared")
add(APP, "R13", "Tapping a person on an item", "",
    [P("test_R13_tapping_a_person_on_an_item"), P("test_R13_tapping_a_person_changes_the_shares")])
add(APP, "R14", "A price error sits in the item line", "", [P("test_R14_a_price_error_sits_in_the_item_line")])
FOCUS_ROWS = [
    ("cold boot, Add person, Person 3 name", [P("test_R34_focus_moves_to_the_name_field_at_the_removed_position[Ben-Chen]")],
     "the test's first assertion, from a cold boot"),
    ("S1, Remove Ben, Person 2 name (Chen)", [D("D4 R34 focus after a click, S1 seed", "row b:")],
     "driven on the S1 seed (D4); the suite test removes Ben from a three-person bill"),
    ("S1, Remove Chen, Person 2 name (Ben)", [D("D4 R34 focus after a click, S1 seed", "row c:")],
     "driven on the S1 seed (D4); the suite test removes Chen from a three-person bill"),
    ("S1, Add item, Item 5 name", [D("D4 R34 focus after a click, S1 seed", "row d:"),
                                   P("test_R34_focus_after_adding_or_removing_an_item[Add item-Item 5 name]")],
     "driven on the S1 seed (D4) with the suite test on the same bill"),
    ("S1, Remove Char kuey teow, Item 2 name (Mee goreng mamak)", [D("D4 R34 focus after a click, S1 seed", "row e:"),
                                                                    P("test_R34_focus_after_adding_or_removing_an_item[Remove Char kuey teow-Item 2 name]")],
     "driven on the S1 seed (D4) with the suite test on the same bill"),
    ("S1, Remove Satay, Item 3 name", [D("D4 R34 focus after a click, S1 seed", "row f:"),
                                       P("test_R34_focus_after_adding_or_removing_an_item[Remove Satay, 10 sticks-Item 3 name]")],
     "driven on the S1 seed (D4) with the suite test on the same bill"),
    ("cold boot, By item, one item, Remove Item 1, Add item", [P("test_R34_removing_the_last_item_focuses_add_item")], ""),
]
for row, refs, note in FOCUS_ROWS:
    add(APP, "R34", "Focus after adding or removing", row, refs, note=note)
for text, pattern_refs in [
        ("Person 1 name, Aisyah", [P("test_R33_typing_in_a_person_name_keeps_focus_and_caret")]),
        ("Item 1 name, Nasi", [P("test_R33_typing_in_an_item_field_keeps_focus_and_caret[<lambda>-Nasi]")]),
        ("Item 1 price in RM, 15.90", [P("test_R33_typing_in_an_item_field_keeps_focus_and_caret[<lambda>-15.90]")]),
        ("Subtotal, 100.00", [P("test_R33_typing_in_an_amount_or_a_rate_keeps_focus_and_caret[subtotal]")]),
        ("Service charge, 12.5", [P("test_R33_typing_in_an_amount_or_a_rate_keeps_focus_and_caret[service-charge]")])]:
    add(APP, "R33", "Typing never loses its place", text, pattern_refs)
add(APP, "R33", "IME composition survives a render", "", [P("test_R33_ime_composition_survives_a_render")])
add(APP, "R15", "The Charges block and its defaults", "", [P("test_R15_charges_block_and_its_defaults")])
add(APP, "R15", "A rate error names both ids and its range", "", [P("test_R15_a_rate_error_names_both_ids_and_its_range")])
add(APP, "R15 R19", "A charge of 0 is allowed and still shown", "", [P("test_R19_a_charge_of_zero_is_allowed_and_still_shown")])
add(APP, "R16", "The panel follows every keystroke and stays quiet", "",
    [P("test_R16_the_panel_follows_every_keystroke_and_stays_quiet"),
     P("test_R16_the_status_is_the_only_live_element_and_only_while_the_table_is")])
for test_id in ["rate-empty", "rate-too-high", "subtotal-empty", "no-items", "item-unpriced", "item-bad-price"]:
    add(APP, "R17", "When the shares cannot be worked out", test_id,
        [P(f"test_R17_when_the_shares_cannot_be_worked_out[{test_id}]")])
add(APP, "R18", "Items that still need a person", "", [P("test_R18_items_that_still_need_a_person")])
for seed in ["S2", "S1"]:
    add(APP, "R19", "The bill summary shows its working", seed, [P(f"test_R19_the_bill_summary_shows_its_working[{seed}]")])
add(APP, "R20", "The even split from a cold boot (key flow 1)", "", [P("test_R20_the_even_split_from_a_cold_boot")])
add(APP, "R21", "The by-item split from gestures (key flow 2)", "", [P("test_R21_the_by_item_split_from_gestures")],
    note="the table heads are checked as +Charges and =Share, the text the golden renders (observation 3)")
add(APP, "R21", "Someone who had nothing is still listed", "", [P("test_R21_someone_who_had_nothing_is_still_listed")])
for seed in ["S2", "S1"]:
    add(APP, "R22", "Copy summary puts the exact text on the clipboard", seed,
        [P(f"test_R22_copy_summary_puts_the_exact_text_on_the_clipboard[{seed}]")])
add(APP, "R23", "The browser blocks the clipboard", "",
    [P("test_R23_the_browser_blocks_the_clipboard"), D("D3 R23 browser blocks the clipboard, S2 seed")],
    note="the suite checks the status and the panel; D3 also checks the draft, the form and the shares rows")
add(APP, "R23", "The clipboard API is missing", "", [P("test_R23_the_clipboard_api_is_missing")])
add(APP, "R24", "The status lives as long as the table", "",
    [P("test_R24_the_status_lives_as_long_as_the_table"), P("test_R24_the_status_is_not_saved")])
for change, test_id in [("type A into Person 1 name", "name"), ("click Add person", "add-person"),
                        ("type 1 into Subtotal", "subtotal"), ("click By item", "mode"),
                        ("click By item, then Add item", "add-item"), ("replace SST with 8", "sst")]:
    add(APP, "R25", "Every change is saved", change, [P(f"test_R25_every_change_is_saved[{test_id}]")])
add(APP, "R25", "Leaving a field or copying does not save", "", [P("test_R25_leaving_a_field_or_copying_does_not_save")])
add(APP, "R26", "Come back later (key flow 3)", "", [P("test_R26_come_back_later")])
for name in ["G1", "G2", "G3"]:
    add(APP, "R26", "Odd but readable drafts load", name, [P(f"test_R26_odd_but_readable_drafts_load[{name}]")])
for number in range(1, 25):
    add(APP, "R27", "An unreadable draft starts a new bill with a note", f"B{number}",
        [P(f"test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B{number}]")])
add(APP, "R27", "Dismissing the note", "",
    [P("test_R27_dismissing_the_note_moves_focus_to_the_first_name"), P("test_R27_the_note_is_not_touched_by_start_over")])
for breaker in ["read-localStorage", "getItem", "setItem"]:
    add(APP, "R28", "The app works without storage", breaker, [P(f"test_R28_the_app_works_without_storage[{breaker}]")])
add(APP, "R29", "The dialog opens with the safe choice focused", "", [P("test_R29_the_dialog_opens_with_the_safe_choice_focused")])
for close in ["cancel", "escape", "backdrop-corner", "backdrop-over-a-field"]:
    add(APP, "R30", "Leaving the dialog without starting over", close,
        [P(f"test_R30_leaving_the_dialog_without_starting_over[{close}]")])
add(APP, "R29", "A repeat press on New bill leaves the dialog open", "360x640, 390x844, 1280x800 by 3 gestures",
    [G("test_R29_a_repeat_press_on_new_bill_leaves_the_dialog_open[*]", 9)],
    note="mouse double, mouse triple and touch double")
for close in ["cancel", "backdrop", "escape"]:
    add(APP, "R30", "After a double click on New bill one deliberate click still closes it", close,
        [P(f"test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it[{close}]")])
add(APP, "R29", "The keyboard and the next press are not held back", "",
    [P("test_R29_opening_by_keyboard_and_opening_again_straight_away_is_not_held_back"),
     P("test_R29_the_guard_of_opening_ends_at_the_next_press")])
add(APP, "R31", "Start over (key flow 4)", "", [P("test_R31_start_over")])
add(APP, "R31", "Start over clears the copy status", "", [P("test_R31_start_over_clears_the_copy_status")])
for field in ["subtotal", "item-price", "service", "sst"]:
    add(APP, "R31", "Start over clears the error flags", field, [P(f"test_R31_start_over_clears_the_error_flags[{field}]")])
for state in ["S3", "S1", "S7"]:
    add(APP, "R32", "Tab order follows the golden", state,
        [P(f"test_R32_tab_order_follows_the_golden_and_every_stop_shows_its_ring[{state}]"),
         P("test_R32_the_ring_check_has_teeth")])
for layout in ["S1-360", "S2-360", "S3-360", "S5-360", "S1-390", "S1-1280", "S3-1280", "M1-360"]:
    add(APP, "R35", "No horizontal overflow at phone and desktop sizes", layout,
        [P(f"test_R35_no_horizontal_overflow_and_the_layout_of_each_size[{layout}]")])
add(APP, "R35", "Sizes the design gives at 360 x 780", "", [P("test_R35_sizes_the_design_gives_at_360_by_780")])
add(APP, "R35", "Content width at 1280 x 800", "", [P("test_R35_content_width_of_the_header_and_the_note_at_1280_by_800")])
for setting, duration in [("reduce", "0s"), ("no-preference", "0.12s, 0.12s")]:
    add(APP, "R36", "Motion follows the user's setting", setting,
        [P(f"test_R36_motion_follows_the_users_setting[{setting}-{duration}]")])
add(APP, "R37", "Names are shown as text, never as markup", "",
    [P("test_R37_names_are_shown_as_text_and_never_as_markup"), P("test_R37_no_banned_api_in_the_shipped_files"),
     P("test_R37_the_banned_api_scan_has_teeth")])
add(APP, "R38", "The Content Security Policy is exact and never violated", "",
    [P("test_R38_policy_is_exact_and_nothing_inline")],
    note="the console rule for the whole suite is enforced by the open_app fixture on every browser test")
add(APP, "R38", "The strict policy blocks nothing the app needs", "S3, cold boot",
    [P("test_R38_strict_policy_blocks_nothing_the_app_needs")])
add(APP, "R38", "The strict policy blocks nothing the app needs", "S1 seed",
    [D("D2 R38 strict policy, S1 seed")], note="the suite test checks only the cold boot row")
add(APP, "R38", "The strict policy blocks nothing the app needs", "S2 seed with the New bill dialog open",
    [D("D2 R38 strict policy, S2 seed with the dialog open")], note="the suite test checks only the cold boot row")
add(APP, "R39", "Nothing leaves the device", "",
    [P("test_R39_nothing_leaves_the_device_by_the_static_scan"), P("test_R39_the_network_scan_has_teeth"),
     P("test_R39_a_whole_session_makes_only_same_origin_gets")])
add(APP, "R39", "The SVG icons come from createElementNS", "",
    [P("test_R39_icons_come_from_createElementNS_and_the_page_holds_its_icons")])
add(APP, "R40", "Looks right", "",
    [GATE("fidelity")],
    untested=("The pixel half passed: the fidelity gate ran through its own code (run_gates.py, the unchanged "
              "tests/browser/fidelity/run.py with its evidence folder moved into this folder) and all 10 pairs match "
              "with 0 mismatching pixels. The other half, every FE element checklist row passes, needs a per-element "
              "review of styles.json, the fidelity finder's step, which this regression did not run. Not counted as a pass."))
add(APP, "R40", "The runner uses the Python that runs pytest", "",
    [P("test_R40_the_runner_uses_the_python_that_runs_pytest")])
add(APP, "R41", "Works right", "", [GATE("live")],
    note="the cold-boot live gate passed all 7 steps; its artifacts are in gates/live-e2e")


# ------------------------------------------------------------------ verdicts
for row in ROWS:
    row["covered_by"] = [check_ref(ref) for ref in row["refs"]]
    row["verdict"] = "UNTESTED" if row["untested"] else "PASS"

counts = Counter(row["verdict"] for row in ROWS)
PASS, FAIL, UNTESTED = counts.get("PASS", 0), counts.get("FAIL", 0), counts.get("UNTESTED", 0)
CORE_ROWS = [r for r in ROWS if r["doc"] == CORE]
APP_ROWS = [r for r in ROWS if r["doc"] == APP]
assert FAIL == 0
assert len(CORE_ROWS) == 179, len(CORE_ROWS)
assert len(APP_ROWS) == 162, len(APP_ROWS)
TOTAL = len(ROWS)
assert TOTAL == 341

# ------------------------------------------------------------------ the table
TABLE_HEAD = ("| # | file | R# | scenario | row | covering test or driven check | verdict | note |\n"
              "|---|------|----|----------|-----|-------------------------------|---------|------|\n")
table_lines = []
for number, row in enumerate(ROWS, start=1):
    covered = " + ".join(row["covered_by"])
    note = row["untested"] if row["untested"] else row["note"]
    table_lines.append(f"| {number} | {row['doc']} | {row['r']} | {row['scenario']} | {row['row']} | {covered} | "
                       f"{row['verdict']} | {note} |")
TABLE = TABLE_HEAD + "\n".join(table_lines) + "\n"
(EVID / "scenario-table.json").write_text(json.dumps(ROWS, indent=2, ensure_ascii=False), encoding="utf-8")
(EVID / "scenario-table.md").write_text(TABLE, encoding="utf-8")

# ------------------------------------------------------------------ the findings file
def group_results(group):
    checks = DRIVEN[group]
    return len(checks), sum(c["result"] == "PASS" for c in checks)


def tag(ok):
    return "PASS" if ok else "FAIL"


d1, d2a = group_results("D1 R5 rename per keystroke, S1 seed"), group_results("D2 R38 strict policy, S1 seed")
d2b = group_results("D2 R38 strict policy, S2 seed with the dialog open")
d3 = group_results("D3 R23 browser blocks the clipboard, S2 seed")
d4 = group_results("D4 R34 focus after a click, S1 seed")
DRIVEN_ALL = [d1, d2a, d2b, d3, d4]
DRIVEN_TOTAL = sum(n for n, _ in DRIVEN_ALL), sum(p for _, p in DRIVEN_ALL)
fid = GATES["fidelity_pairs"]
live = GATES["live_summary"]
flow_checks = DRIVEN_FILES["flows.py"]["checks"]
flow_groups = {}
for check in flow_checks:
    flow_groups.setdefault(check["group"], Counter())[check["result"]] += 1
FLOW = DRIVEN_FILES["flows.py"]["counts"]
folder_files = sorted(p.name for p in EVID.iterdir() if p.is_file())
FID_FOLDER = Path(GATES["fidelity_run_folder"]).name
LIVE_FOLDER = Path(GATES["live_run_folder"]).name
PAIRS_PASS = sum(1 for p in fid.values() if p["dimensions_match"] is True and p["mismatch_pixels"] == 0)
doc_counts = {doc: Counter(r["verdict"] for r in rows) for doc, rows in ((CORE, CORE_ROWS), (APP, APP_ROWS))}

frontmatter = f"""---
module: split-app
kind: qa
run: regression
status: pass
counts: {{ pass: {PASS}, fail: {FAIL}, untested: {UNTESTED} }}
---
"""

verdict = f"""# Regression QA: split (split-core and split-app), v1.0.0

## Verdict

PASS, with {UNTESTED} untested item and {FAIL} failures. Scenario items: {PASS} pass, {FAIL} fail, {UNTESTED} untested, of {TOTAL} in total.
split-core gives {doc_counts[CORE]['PASS']} of {len(CORE_ROWS)} pass. split-app gives {doc_counts[APP]['PASS']} of {len(APP_ROWS)} pass and {doc_counts[APP]['UNTESTED']} untested.
The untested item is R40 "Looks right" (split-app). Its pixel half passed (all {PAIRS_PASS} fidelity pairs, 0 mismatching pixels). Its FE element checklist half was not judged in this run.

Suites. Node {NODE_COUNTS['pass']} of {NODE_COUNTS['tests']} pass and {NODE_COUNTS['fail']} fail. Browser {SUITES['pytest_browser']['passed']} passed, {SUITES['pytest_browser']['failed']} failed, {SUITES['pytest_browser']['errors']} errors.
Five hand-driven flows at 390 x 844 give {FLOW['pass']} checks passing, {FLOW['fail']} failing, and {FLOW['note']} observations. Driven checks D1 to D4 give {DRIVEN_TOTAL[1]} of {DRIVEN_TOTAL[0]} passing. Gates. The fidelity gate passed {PAIRS_PASS} of {len(fid)} pairs and the live gate passed {live['steps']} of {live['steps']} steps.

The counts in the frontmatter are for the scenario table only: both qa.md files, one item per scenario and one item per outline row.
"""

suites = f"""## 1. Suites

Each suite ran once. The node run is in node-test.txt and the browser run is in pytest.txt.

| Suite | Command | Result | Time | Evidence |
|-------|---------|--------|------|----------|
| split-core unit tests | `node --test "tests/**/*.test.js"` | {NODE_COUNTS['tests']} tests, {NODE_COUNTS['pass']} pass, {NODE_COUNTS['fail']} fail, {NODE_COUNTS['skipped']} skipped, {NODE_COUNTS['todo']} todo | {NODE_DURATION:.0f} ms by the runner's own duration_ms | node-test.txt |
| split-app browser suite | `python -m pytest tests/browser -q -p no:cacheprovider` | {SUITES['pytest_browser']['passed']} passed, {SUITES['pytest_browser']['failed']} failed, {SUITES['pytest_browser']['errors']} errors ({len(COLLECT)} collected) | {SUITES['pytest_browser']['last_line'].split(' in ')[1].split(' (')[0]} by pytest ({SUITES['pytest_browser']['seconds_wall']} s wall) | pytest.txt, junit.xml, pytest-collect.txt |

The first attempt at the node summary (run_suites.py) crashed after the node suite had finished, on a regex for the
reporter's summary lines. The saved node output is the node run's record, and the node suite was not run again.
The browser suite's server started and stopped with its port free (pytest.txt).
"""

scenario_intro = f"""## 2. Scenario table

Counting. Each non-outline scenario is one item. Each Examples row of a scenario outline is one item, so a single outline with four rows counts as four. split-core qa.md has 54 scenarios (21 outlines) and gives {len(CORE_ROWS)} items. split-app qa.md has 78 scenarios (25 outlines) and gives {len(APP_ROWS)} items. A scenario with several Then clauses is one item, and the note says where a clause rests on a driven check.

Covering tests are named as the file and the test name. A pattern with * stands for the parameters, and the count of ids is given in brackets. Every cited test was looked up in the saved outputs before its row was written (build_findings.py): node tests in node-test.txt, pytest tests in junit.xml, driven checks in their JSON files. The same table is in scenario-table.md.

{TABLE}"""

driven_section = f"""## 3. Driven checks

These cover the parts of scenarios that no passing suite test covers exactly, and the two gates that the suite does not run.
Each was driven on the real page (headless Chromium, real clicks and keys), or by the gate's own code.

| Check | Script and output | Covers | Checks | Result | What was seen |
|-------|-------------------|--------|--------|--------|---------------|
| D1 | driven_checks.py, driven-checks.json | R5, renaming on each keystroke, S1 seed | {d1[0]} | {tag(d1[1] == d1[0])} | Typing " Wei" after Chen. On each key all four toggles, the shares row and the remove button read the trimmed label. Line 5 of the copied text is "Chen Wei RM 24.48". |
| D2 (S1) | driven_checks.py, driven-checks.json | R38, strict policy, S1 seed | {d2a[0]} | {tag(d2a[1] == d2a[0])} | Body background rgb(238, 240, 238). Three people rows and two Charges inputs. The S1 table and check row. No style attribute under body. No CSP message and no page error. |
| D2 (S2) | driven_checks.py, driven-checks.json | R38, strict policy, S2 seed with the dialog open | {d2b[0]} | {tag(d2b[1] == d2b[0])} | Dialog open, the same background, the S2 table and check row under it, no style attribute, no CSP message, no page error. |
| D3 | driven_checks.py, driven-checks.json | R23, blocked clipboard keeps the bill, S2 seed | {d3[0]} | {tag(d3[1] == d3[0])} | Status "Could not copy. Your browser blocked the clipboard." with class "status status-failure". The draft text, the form state, the shares rows, the check row and the panel (less the status line) are unchanged. |
| D4 | driven_r34.py, driven-r34.json | R34, focus rows b to f, S1 seed | {d4[0]} (3 per row) | {tag(d4[1] == d4[0])} | Focus lands on Person 2 name (Chen), Person 2 name (Ben), Item 5 name (empty), Item 2 name (Mee goreng mamak) and Item 3 name (Mee goreng mamak). |
| G1 (R40) | run_gates.py, gates/fidelity/{FID_FOLDER} | R40, Looks right, pixel half | {len(fid)} pairs | {PAIRS_PASS} of {len(fid)} PASS | Every pair has dimensions_match true and 0 mismatching pixels (bill-empty, bill-even, bill-items, bill-unassigned and new-bill-dialog at 390 x 844 and 1280 x 800). The per-element checklist half was not judged here. |
| G2 (R41) | run_gates.py, gates/live-e2e/{LIVE_FOLDER} | R41, Works right, cold-boot live gate | {live['steps']} steps | PASS | Steps 1 to 7 pass: cold boot, even split, copy, by item and copy, come back, start over and reload, and step 7, which covers zero console errors, zero page errors, no Content Security Policy violation, and same-origin GETs only. |

The gates ran through their own code with their evidence folder moved into this folder, so the normal evidence folders under docs/modules/split-app/qa/ were not written. The verdicts are the gates' own verdict files.
"""

flows_section = f"""## 4. Five hand-driven flows at 390 x 844

Served by `python -m http.server` on a free loopback port from the project root. Each flow runs in one browser context with empty storage (no seed), the suite's clipboard recorder, and only real clicks, typed keys and key presses. The final run is flows.json. The earlier attempts are kept beside it, as observation 1 explains.

| Flow | Checks | Result | What was seen |
|------|--------|--------|---------------|
| 1 even split | {sum(flow_groups['F1 even split'].values())} | {tag(flow_groups['F1 even split']['FAIL'] == 0)} | Aisyah, Ben and Chen typed by hand, Subtotal 100.00. Aisyah RM 38.87, Ben RM 38.87, Chen RM 38.86, "Adds up to" RM 116.60. Default charges 10 and 6. Summary Service RM 10.00 (10% of RM 100.00) and SST RM 6.60 (6% of RM 110.00). Copy summary gives the status "Summary copied", the recorder holds the S2 block exactly, with one write. Screenshot flow1-even-split-end.png. |
| 2 by item | {sum(flow_groups['F2 by item'].values())} | {tag(flow_groups['F2 by item']['FAIL'] == 0)} | Four items typed with prices and taps, and who had each as expected. Shares Aisyah RM 29.04, Ben RM 15.74 and Chen RM 24.48. The three add up to the Total RM 69.26 (6926 sen). The items column adds up to RM 59.40 and the charges column to RM 9.86. Screenshot flow2-by-item-end.png. |
| 3 a wrong price | {sum(flow_groups['F3 a wrong price'].values())} | {tag(flow_groups['F3 a wrong price']['FAIL'] == 0)} | "abc" typed in a price gives no error while typing, and the panel says "Give every item a price". Tab shows the error "Enter an amount like 12.50" with aria-invalid true, and the panel still waits. Fixed to 10.00, the error goes, focus stays, the bill summary shows (RM 10.00, 1.00, 0.66, total 11.66) and the panel asks for a person. Tapping Aisyah gives Aisyah RM 10.00, RM 1.66, RM 11.66. Screenshots flow3-error-shown.png and flow3-wrong-price-end.png. |
| 4 come back | {sum(flow_groups['F4 come back'].values())} | {tag(flow_groups['F4 come back']['FAIL'] == 0)} | Reload leaves the form, the stored draft and the shares as they were. New bill opens a modal dialog with Cancel focused. Cancel closes it, keeps the bill and the stored draft, and returns focus to New bill. Start new bill gives people Person 1 and Person 2, an empty subtotal, Even, charges 10 and 6, the even message, and the stored draft is the new bill. Screenshots flow4-reloaded.png and flow4-come-back-end.png. |
| 5 double presses | {sum(flow_groups['F5 double presses'].values()) + sum(flow_groups['F5 double presses, chip under a pending price error'].values())} | {tag(flow_groups['F5 double presses']['FAIL'] + flow_groups['F5 double presses, chip under a pending price error']['FAIL'] == 0)} | A: a double click on Add person from a cold boot adds exactly one person (3 rows, nextId 4, focus on Person 3 name). B: with eight people and the four S1 items, "abc" typed in item 1's price and left, a double click on the item 2 chip that lies under its own Remove (the first of 24 points, at 329.5, 733). The items stay at four with the same ids. The first click toggled one chip (Farid on), and the repeat press removed nothing. Screenshots flow5a-double-add-person.png and flow5b-double-click-chip-end.png. |

Flow 5 part B is the RG-CR-08 fix. It was probed at scrollY 0 on the 390 x 844 page, with the points measured in the same state the press was made in. probe-chips.json and probe-scout.json are the diagnostic runs that show why the bill has four items.
"""

observations = """## 5. Observations

1. Flow attempts. Three earlier flow runs are kept beside flows.json. Attempt 1 (flows-attempt-1.json) failed on two defects in my script. One expectation ignored that R18 keeps the bill summary on screen while an item has no person, and one check had no "what" argument. Attempt 2 (flows-attempt-2-one-item.json) used a one-item bill, which has no item 2 whose Remove lies under its chips after an error, so part B found no point. Attempt 3 (flows-attempt-3-stale-scroll.json) measured the chips before a click had scrolled the page, so the points were stale. Each was fixed in the script. The app was not changed in any attempt.
2. The node summary parser in run_suites.py failed after the node suite had finished. The saved node output (node-test.txt) is the record and was used. The node suite was not run a second time.
3. The table heads read "+Charges" and "=Share" as text. The golden bill-items.html has the same markup, with the plus sign in a span marked aria-hidden and no space after it, so the app matches the golden. qa.md writes "+ Charges" as notation. Not a finding.
4. With an item priced and nobody tapped, the bill summary stays on screen with its totals, and the Shares section gives the "1 item still needs a person" message. R18 says exactly this, so it is expected.
5. The RG-CR-08 probe finds points only for item 2's Remove (the first at 329.5, 733). The double press there removed nothing, and the one chip it touched toggled once (Farid went on). That is one real click followed by a cancelled repeat press, which is the intended behaviour.
6. The fidelity harness renders with its own CSP bypass, as qa.md says. So the 10 pixel passes say nothing about the policy. The functional suite and the live gate keep the policy live and cover it.
7. The gate evidence for this run is under gates/ in this folder. The normal gate folders under docs/modules/split-app/qa/ (fidelity and live-e2e) were not written by this run. Earlier runs from today are still there, for example qa/fidelity/20261010-123651. If the orchestrator needs the gates in their normal place, they should be run there.
8. Two node test files, draft.test.js and errors.test.js, are not in the split-core qa.md file list. Their titles carry R10, R26, R27 and R28, and all of them pass, so they are extra coverage.
9. Several split-app rows are covered by a test that builds the S1 bill by gestures, where qa.md names the S1 seed. The seeded and the gesture-built bills show the same screen, since both match bill-items.html in the R3 walks, so these rows count as covered. The rows where a suite test did not check the seed's exact state were driven (D1, D2 and D4).
10. Nothing in the run wrote into qa/functional. SPLIT_EVIDENCE was unset for every suite run, and the suite wrote no failure screenshot.
11. The copy text checked by the suite and by flow 1 matches the S2 and S1 blocks in split-core spec R24.
12. The R2 never-throws test draws its characters from a seeded alphabet that has one space where qa.md lists two, before the fullwidth digit. The space is already in the alphabet, so the Then is still exercised over 500 strings. The row is PASS with this note. A reader who wants the exact alphabet should add the second space to the test, which this run did not change.
"""

evidence_section = f"""## 6. Evidence

Folder: docs/modules/split-app/qa/regression-qa/20261010T124914/. The index is evidence.md.
Files in the folder when this report was built: {', '.join(folder_files)}.
Screenshots: flows/ (8 files), driven/ (5 files) and probe-chips-after-error.png.
Gate outputs: gates/fidelity/{FID_FOLDER}/ (10 pair folders and run.log) and gates/live-e2e/{LIVE_FOLDER}/ (steps.log, summary.json, 7 screenshots, console.log, network.log and the clipboard files).
"""

processes = """## 7. Processes

Every server and browser this run started. Each server printed STOPPED with its port free afterwards.

| Started by | Process | Pid | Port | Stopped |
|------------|---------|-----|------|---------|
| run_browser.py (pytest suite) | python -m http.server (fixture) | 13352 | 54748 | yes, port free |
| run_browser.py (pytest suite) | Chromium, opened and closed by the pytest session | not recorded by the suite | none | closed at session end |
| run_suites.py | node --test, no server or browser | none | none | n/a |
| driven_checks.py | python -m http.server | 21144 | 48732 | yes, port free |
| driven_checks.py | Chromium 149.0.7827.55 | 15616 | none | closed, none left |
| flows.py attempt 1 | python -m http.server | 16640 | 36765 | yes, port free |
| flows.py attempt 1 | Chromium | 8836 | none | closed, none left |
| flows.py attempt 2 | python -m http.server | 11912 | 63751 | yes, port free |
| flows.py attempt 2 | Chromium | 24396 | none | closed, none left |
| flows.py attempt 3 | python -m http.server | 13368 | 1899 | yes, port free |
| flows.py attempt 3 | Chromium | 4516 | none | closed, none left |
| flows.py final | python -m http.server | 23236 | 47616 | yes, port free |
| flows.py final | Chromium | 10796 | none | closed, none left |
| probe_chips.py | python -m http.server and Chromium | 4036 | 13458 | yes, port free, Chromium closed |
| probe_scout.py | python -m http.server and Chromium | 7112 | 4119 | yes, port free, Chromium closed |
| driven_r34.py | python -m http.server | 7644 | 18118 | yes, port free |
| driven_r34.py | Chromium 149.0.7827.55 | 480 | none | closed, none left |
| run_gates.py, fidelity gate | python -m http.server (run.py's StaticServer) | 2880 | 38267 | yes, port free |
| run_gates.py, fidelity gate | fidelity.py harness, one Chromium per pair (10 runs) | per run, not recorded | none | each run closed its browser |
| run_gates.py, live gate | python -m http.server | 17268 | 14669 | yes, port free |
| run_gates.py, live gate | Chromium | not recorded | none | closed by the gate |

Final check, run after the last script: a query for Playwright Chromium processes returned an empty list, so none was left running.
"""

BODY = "\n".join([verdict, suites, scenario_intro, driven_section, flows_section, observations, evidence_section, processes])
FINDINGS.parent.mkdir(parents=True, exist_ok=True)
FINDINGS.write_text(frontmatter + "\n" + BODY, encoding="utf-8")
print(f"items {TOTAL}: pass {PASS}, fail {FAIL}, untested {UNTESTED}; core {dict(doc_counts[CORE])}, app {dict(doc_counts[APP])}")
print(f"wrote {FINDINGS}")
