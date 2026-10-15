"""Seed drafts for the browser tests (qa.md, "Seed drafts"). This file is the one source.

The fidelity seed scripts in fidelity/ repeat S1, S2, S5, RE, W1, T12, ONE, RND and UNREADABLE["B1"] after the
clipboard stand-in, and test_R40_fidelity_seeds_match keeps them equal (task A19).
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
K1_8 = changed(S1, lambda d: (d["bill"]["people"].extend(
    {"id": f"p{n}", "name": name} for n, name in enumerate(["Devi", "Farid", "Grace", "Hafiz", "Indra"], start=8)),
    d["bill"].update(nextId=13)))  # [K1-8]
T12 = dump({"version": 2, "bill": {
    "mode": "even", "people": [{"id": f"p{n}", "name": name} for n, name in enumerate(["Aisyah", "Ben", "Chen"] + [""] * 9, start=1)],
    "subtotalText": "100.00", "items": [], "serviceText": "10", "sstText": "6", "spare": {"rule": "top"}, "nextId": 13,
}})  # [T12]
T12W = changed(T12, lambda d: [person.update(name="W" * 20) for person in d["bill"]["people"]])  # [T12W] no one name fits at 360
T12I = changed(T12, lambda d: d["bill"].update(mode="item", nextId=14, items=[
    {"id": "i13", "name": "Tea", "priceText": "12.00", "who": [f"p{n}" for n in range(1, 13)]}]))  # [T12I] by item, twelve people
# [I2] core qa example I2. Aisyah had nothing, so she is listed with RM 0.00 and "0.00 + 0.00" (spec R21).
I2 = dump({"version": 2, "bill": {
    "mode": "item", "people": [{"id": "p1", "name": "Aisyah"}, {"id": "p2", "name": "Ben"}, {"id": "p3", "name": "Chen"}],
    "subtotalText": "", "items": [{"id": "i4", "name": "X", "priceText": "10.00", "who": ["p2"]},
                                  {"id": "i5", "name": "Y", "priceText": "5.01", "who": ["p2", "p3"]}],
    "serviceText": "10", "sstText": "6", "spare": {"rule": "top"}, "nextId": 6,
}})

_TWELVE = ["Aisyah", "Ben", "Chen", "Devi", "Farid", "Grace", "Hafiz", "Indra", "Jia Hui", "Kumar", "Lina", "Mei Ling"]
S8 = dump({"version": 2, "bill": {
    "mode": "even", "subtotalText": "", "items": [], "serviceText": "10", "sstText": "6", "spare": {"rule": "top"}, "nextId": 13,
    "people": [{"id": f"p{n}", "name": name} for n, name in enumerate(_TWELVE, start=1)],
}})
# [MAX-E] and [MAX-I], split-core qa's named bills at the money ceiling, people named as S8 (spec R60, task A18). Items
# have blank names, item k (0-based) is had by person k mod 12.
MAX_E = changed(S8, lambda d: d["bill"].update(subtotalText="99999.99", serviceText="30", sstText="20"))
MAX_I = changed(S8, lambda d: d["bill"].update(mode="item", serviceText="30", sstText="20", nextId=63, items=[
    {"id": f"i{13 + k}", "name": "", "priceText": "99999.99", "who": [f"p{k % 12 + 1}"]} for k in range(50)]))

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
    # D13, the spare choice (task A3, qa.md B25 to B32)
    "B25": changed(S2, lambda d: d["bill"].pop("spare")),
    "B26": with_bill(S2, spare={"rule": "two"}),
    "B27": with_bill(S2, spare={"rule": "one", "personId": "p9"}),
    "B28": with_bill(S2, spare={"rule": "one"}),
    "B29": with_bill(S2, spare={"rule": "random", "order": ["p1", "p2"]}),
    "B30": with_bill(S2, spare={"rule": "random", "order": ["p1", "p1", "p2", "p3"]}),
    "B31": with_bill(S2, spare={"rule": "random", "order": ["p1", "p2", "p3", "p4"]}),
    "B32": with_bill(S2, spare=[]),
}

# [PA0] Two spare sen, and every order gives Aisyah RM 0.01, Ben RM 0.01, Chen RM 0.00, so Pick again can change nothing.
PA0 = dump({"version": 2, "bill": {
    "mode": "item", "people": [{"id": "p1", "name": "Aisyah"}, {"id": "p2", "name": "Ben"}, {"id": "p3", "name": "Chen"}],
    "subtotalText": "", "items": [{"id": "i4", "name": "X", "priceText": "0.01", "who": ["p1", "p2"]},
                                  {"id": "i5", "name": "Y", "priceText": "0.01", "who": ["p1", "p2"]}],
    "serviceText": "0", "sstText": "0", "spare": {"rule": "random", "order": ["p1", "p2", "p3"]}, "nextId": 6,
}})

# Readable drafts that look odd (must load, R26 with D8, D11, D12). Id -> stored text.
ODD_READABLE = {
    "G1": changed(S2, lambda d: (d.update(extra=1), d["bill"]["people"][0].update(colour="red"))),
    "G2": changed(S2, lambda d: d["bill"]["people"][0].update(name=FLAGS_20)),
    # json.dumps writes "__proto__" as an ordinary key; the page's JSON.parse makes it an own property.
    "G3": changed(S2, lambda d: d["bill"].update({"__proto__": {"polluted": True}})),
}
# [S2_V1] and [S1_V1], drafts saved by 1.0: version 1 and no spare key.
S2_V1 = changed(S2, lambda d: (d.update(version=1), d["bill"].pop("spare")))
S1_V1 = changed(S1, lambda d: (d.update(version=1), d["bill"].pop("spare")))
ODD_READABLE.update({
    # Ben is on no item, so his One person choice falls back to Top of the list and stays stored (CG-P7).
    "G4": changed(S1, lambda d: (d["bill"].update(spare={"rule": "one", "personId": "p2"}), d["bill"]["items"][1].update(who=["p1"]))),
    "G5": changed(S2_V1, lambda d: d["bill"].update(spare={"rule": "random", "order": ["p1"]})),
    "G6": with_bill(S2, spare={"rule": "top", "extra": 1}),
    "G7": S1_V1,
})

# [G8] K2 with bidi and separator characters in four names (qa.md, R62, H-10), each one written as its JSON escape,
# as a draft written by hand or by another page may hold it. Not in ODD_READABLE, its own scenario reads it.
G8 = json.dumps(json.loads(changed(S2, lambda d: d["bill"].update(nextId=6, people=[
    {"id": "p1", "name": "Aisyah"}, {"id": "p2", "name": "Ben\u202E"}, {"id": "p3", "name": "Chen\u2067"},
    {"id": "p4", "name": "A\u2028B"}, {"id": "p5", "name": "\u202E"}]))), separators=(",", ":"), ensure_ascii=True)
