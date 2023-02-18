# Print all Unicode characters in the range 0A80—0AFF (all Gujarati Unicode)
d = {}
for x in range(int("0A80", 16), int("0AFF", 16) + 1):
    d[hex(x)] = " " + chr(x) + " "
print(d)
