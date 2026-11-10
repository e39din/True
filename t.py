import not_true
text = "= args\nmy name is ${=> name} and surname is ${=> surname}\n= main\n"
f = not_true.parse_fn_file(text)
print(f)
print(f["main"].body)