import tests
src = open(tests.__file__, encoding="utf-8").read()
i = src.find("T137")
print(repr(src[i-400:i+200]))
print("FN_CHAIN in NT.parse:", "FN_CHAIN" in src)