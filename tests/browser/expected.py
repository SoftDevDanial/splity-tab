"""What the functional suite (test_app.py) and the live gate (live_e2e.py) both expect to see and to copy.

One source, so the two cannot drift apart and no test is needed to keep copies equal. The copy blocks are the S2 and
S1 blocks of split-core spec R24, and the figures are the ones qa.md gives for the S2 and S1 bills. Test-side only,
never loaded by index.html.
"""

# What the v1.1.0 card reads for a blocked result, by the result's reason (spec R17, qa.md "the card reads").
BLOCKED_CARD = {
    "rates": "Total Check the charges to see the splits.",
    "subtotal": "Total Enter the subtotal to see the splits.",
    "no-prices": "Total Add each item and tap who had it to see the splits.",
    "prices": "Total Give every item a price to see the splits.",
}

# The bill-empty screen of a cold boot (spec R2, with R48's open People and folded Charges), as support.cold_boot_state
# reads it. The live gate asserts it at steps 1 and 8 (qa.md, "Cold-boot live-e2e gate").
COLD_BOOT = {
    "names": ["Person 1", "Person 2"], "removesDisabled": [True, True], "evenChecked": True, "subtotal": ["", "0.00"],
    "subtotalErrorHidden": True, "rates": ["10", "6"], "open": ["true", "true", "false"],
    "card": BLOCKED_CARD["subtotal"], "totalHolds": ["span.r-label"], "emptyIcon": "#i-mark",
    "strip": "Enter the subtotal to see the splits.", "stripCopy": {"shown": True, "disabled": True},
}

# What the v1.1.0 card holds for the S1 (K1) and S2 (K2) bills (spec R19 to R21): the bill lines, each splits row as its
# name, amount and working with the hidden words left out (None in even mode), and the proof as its amount and working.
S1_LINES = [["Subtotal", "RM 59.40"], ["Service 10%", "RM 5.94"], ["SST 6%", "RM 3.92"]]
S1_SPLITS = [["Aisyah", "RM 29.04", "24.90 + 4.14"], ["Ben", "RM 15.74", "13.50 + 2.24"], ["Chen", "RM 24.48", "21.00 + 3.48"]]
S1_PROOF = ["RM 69.26", "59.40 + 9.86"]
S2_LINES = [["Subtotal", "RM 100.00"], ["Service 10%", "RM 10.00"], ["SST 6%", "RM 6.60"]]
S2_SPLITS = [["Aisyah", "RM 38.87", None], ["Ben", "RM 38.87", None], ["Chen", "RM 38.86", None]]
S2_PROOF = ["RM 116.60", None]

# S1 (K1): Aisyah, Ben and Chen, By item, the four items with their prices and who had them.
S1_ITEMS = [("Nasi lemak ayam", "15.90", ["Aisyah"]), ("Char kuey teow", "13.50", ["Ben"]),
            ("Mee goreng mamak", "12.00", ["Chen"]), ("Satay, 10 sticks", "18.00", ["Aisyah", "Chen"])]
S1_COPY = ("Bill split\nTotal RM 69.26 (subtotal RM 59.40, service 10% RM 5.94, SST 6% RM 3.92)\n"
           "Aisyah RM 29.04\nBen RM 15.74\nChen RM 24.48\nAdds up to RM 69.26")

# S2 (K2): Aisyah, Ben and Chen, Even, subtotal 100.00.
S2_COPY = ("Bill split\nTotal RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)\n"
           "Aisyah RM 38.87\nBen RM 38.87\nChen RM 38.86\nAdds up to RM 116.60")
