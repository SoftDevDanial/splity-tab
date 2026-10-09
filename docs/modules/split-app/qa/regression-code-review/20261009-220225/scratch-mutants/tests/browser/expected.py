"""What the functional suite (test_app.py) and the live gate (live_e2e.py) both expect to see and to copy.

One source, so the two cannot drift apart and no test is needed to keep copies equal. The copy blocks are the S2 and
S1 blocks of split-core spec R24, and the figures are the ones qa.md gives for the S2 and S1 bills. Test-side only,
never loaded by index.html.
"""

# The panel of a new bill: only the Shares heading and the message (S3, bill-empty).
EVEN_MESSAGE = "Shares\nEnter the subtotal to see the shares."

# S1: Aisyah, Ben and Chen, By item, four items and who had them.
S1_ITEMS = [("Nasi lemak ayam", "15.90", ["Aisyah"]), ("Char kuey teow", "13.50", ["Ben"]),
            ("Mee goreng mamak", "12.00", ["Chen"]), ("Satay, 10 sticks", "18.00", ["Aisyah", "Chen"])]
S1_SUMMARY = [["Subtotal", "RM 59.40", ""], ["+Service charge", "RM 5.94", "10% of RM 59.40"],
              ["+SST", "RM 3.92", "6% of RM 65.34"], ["=Total", "RM 69.26", ""]]
S1_ROWS = [["Aisyah", "RM 24.90", "RM 4.14", "RM 29.04"], ["Ben", "RM 13.50", "RM 2.24", "RM 15.74"],
           ["Chen", "RM 21.00", "RM 3.48", "RM 24.48"]]
S1_CHECK = [["Adds up to", "RM 59.40", "RM 9.86", "RM 69.26"]]
S1_COPY = ("Bill split\nTotal RM 69.26 (subtotal RM 59.40, service 10% RM 5.94, SST 6% RM 3.92)\n"
           "Aisyah RM 29.04\nBen RM 15.74\nChen RM 24.48\nAdds up to RM 69.26")

# S2: Aisyah, Ben and Chen, Even, subtotal 100.00.
S2_SUMMARY = [["Subtotal", "RM 100.00", ""], ["+Service charge", "RM 10.00", "10% of RM 100.00"],
              ["+SST", "RM 6.60", "6% of RM 110.00"], ["=Total", "RM 116.60", ""]]
S2_ROWS = [["Aisyah", "RM 38.87"], ["Ben", "RM 38.87"], ["Chen", "RM 38.86"]]
S2_CHECK = [["Adds up to", "RM 116.60"]]
S2_COPY = ("Bill split\nTotal RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)\n"
           "Aisyah RM 38.87\nBen RM 38.87\nChen RM 38.86\nAdds up to RM 116.60")
