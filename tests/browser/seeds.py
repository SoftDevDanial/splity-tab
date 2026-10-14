"""Seed drafts for the browser tests (qa.md, "Seed drafts"). This file is the one source.

The fidelity setup scripts in fidelity/ repeat S1, S2 and S5, and a test keeps them equal. Since task A1 the seeds
here are version 2 and the scripts still hold the version 1 texts, so that test waits for task A19, which rewrites them.
Test-side only: nothing here is loaded by the app, and no seed lives under src/.
"""
import copy
import json


def dump(value):
    """The compact JSON text the app itself writes (JSON.stringify without spaces)."""
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


S2 = (
    '{"version":2,"bill":{"mode":"even","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},'
    '{"id":"p3","name":"Chen"}],"subtotalText":"100.00","items":[],"serviceText":"10","sstText":"6","spare":{"rule":"top"},"nextId":4}}'
)
S1 = (
    '{"version":2,"bill":{"mode":"item","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},'
    '{"id":"p3","name":"Chen"}],"subtotalText":"","items":['
    '{"id":"i4","name":"Nasi lemak ayam","priceText":"15.90","who":["p1"]},'
    '{"id":"i5","name":"Char kuey teow","priceText":"13.50","who":["p2"]},'
    '{"id":"i6","name":"Mee goreng mamak","priceText":"12.00","who":["p3"]},'
    '{"id":"i7","name":"Satay, 10 sticks","priceText":"18.00","who":["p1","p3"]}],'
    '"serviceText":"10","sstText":"6","spare":{"rule":"top"},"nextId":8}}'
)


def changed(seed, edit):
    """A copy of a seed text after edit(draft) changed the parsed draft in place."""
    draft = json.loads(seed)
    edit(draft)
    return dump(draft)


def with_bill(seed, **fields):
    """A copy of a seed with some bill fields replaced, e.g. with_bill(S2, subtotalText="0")."""
    return changed(seed, lambda draft: draft["bill"].update(fields))


S5 = changed(S1, lambda d: d["bill"]["items"][2].update(who=[]))
# The other qa.md seeds the R3 walk reaches its goldens from (qa.md names in brackets).
ONE = changed(S2, lambda d: d["bill"].update(spare={"rule": "one", "personId": "p2"}))  # [ONE]
RND = changed(S2, lambda d: d["bill"].update(spare={"rule": "random", "order": ["p2", "p3", "p1"]}))  # [RND]
RE = with_bill(S1, serviceText="35")  # [RE]
W1 = changed(S1, lambda d: (d["bill"]["items"].append({"id": "i8", "name": "", "priceText": "964.50", "who": ["p1"]}),
                            d["bill"].update(nextId=9)))  # [W1]
T12 = dump({"version": 2, "bill": {
    "mode": "even", "people": [{"id": f"p{n}", "name": name} for n, name in enumerate(["Aisyah", "Ben", "Chen"] + [""] * 9, start=1)],
    "subtotalText": "100.00", "items": [], "serviceText": "10", "sstText": "6", "spare": {"rule": "top"}, "nextId": 13,
}})  # [T12]

_TWELVE = ["Aisyah", "Ben", "Chen", "Devi", "Farid", "Grace", "Hafiz", "Indra", "Jia Hui", "Kumar", "Lina", "Mei Ling"]
S8 = dump({"version": 2, "bill": {
    "mode": "even", "subtotalText": "", "items": [], "serviceText": "10", "sstText": "6", "spare": {"rule": "top"}, "nextId": 13,
    "people": [{"id": f"p{n}", "name": name} for n, name in enumerate(_TWELVE, start=1)],
}})

FLAGS_20 = "\U0001F1F2\U0001F1FE" * 20  # 20 grapheme clusters, 80 UTF-16 code units


def _people(draft, count):
    draft["bill"]["people"] = [{"id": f"p{n}", "name": f"P{n}"} for n in range(1, count + 1)]
    draft["bill"]["nextId"] = count + 1


def _many_items(draft, count):
    base = copy.deepcopy(draft["bill"]["items"][0])
    draft["bill"]["items"] = [dict(base, id=f"i{n}") for n in range(4, 4 + count)]
    draft["bill"]["nextId"] = 4 + count


def _dup_items(draft):
    draft["bill"]["items"][1]["id"] = "i4"


# Unreadable drafts (each must give the S7 note, R27). Id -> stored text.
UNREADABLE = {
    "B1": "not json",
    "B2": "[]",
    "B3": "null",
    "B4": changed(S2, lambda d: d.update(version=3)),
    "B5": changed(S2, lambda d: d.update(version="2")),
    "B6": '{"version":1,"bill":[]}',
    "B7": with_bill(S2, mode="split"),
    "B8": changed(S2, lambda d: d["bill"].update(people=d["bill"]["people"][:1])),
    "B9": changed(S2, lambda d: _people(d, 13)),
    "B10": changed(S2, lambda d: d["bill"]["people"][0].update(id="x1")),
    "B11": changed(S2, lambda d: d["bill"]["people"][1].update(id="p1")),
    "B12": changed(S2, lambda d: d["bill"]["people"][0].update(name=5)),
    "B13": changed(S1, lambda d: d["bill"]["items"][0].update(who=["p9"])),
    "B14": changed(S1, lambda d: d["bill"]["items"][0].update(who=["p1", "p1"])),
    "B15": changed(S1, lambda d: _many_items(d, 51)),
    "B16": changed(S1, _dup_items),
    "B17": changed(S1, lambda d: d["bill"]["items"][0].update(priceText=15.9)),
    "B18": changed(S2, lambda d: d["bill"]["people"][0].update(name="ABCDEFGHIJKLMNOPQRSTU")),
    "B19": changed(S2, lambda d: d["bill"]["people"][0].update(name="Ai\nsyah")),
    "B20": changed(S1, lambda d: d["bill"]["items"][0].update(name="x" * 41)),
    "B21": with_bill(S2, subtotalText=100),
    "B22": with_bill(S2, nextId=3),
    "B23": with_bill(S2, nextId=1.5),
    "B24": with_bill(S2, nextId=2000000000),
}

# Readable drafts that look odd (must load, R26 with D8, D11, D12). Id -> stored text.
ODD_READABLE = {
    "G1": changed(S2, lambda d: (d.update(extra=1), d["bill"]["people"][0].update(colour="red"))),
    "G2": changed(S2, lambda d: d["bill"]["people"][0].update(name=FLAGS_20)),
    # json.dumps writes "__proto__" as an ordinary key; the page's JSON.parse makes it an own property.
    "G3": changed(S2, lambda d: d["bill"].update({"__proto__": {"polluted": True}})),
}
