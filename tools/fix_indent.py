from pathlib import Path
import re

directories = [Path().cwd()]
files = []

while directories:
	directory = directories.pop(0)
	for e in directory.iterdir():
		if e.is_file() and e.suffix == ".html":
			files.append(e)
		elif e.is_dir():
			directories.append(e)

for f in files:
	print(f"Fixing {f.name}...", end=" ")
	with open(f, "r") as file:
		contents = file.read()
	
	spaces = re.findall(r"\n +", contents)
	if not spaces:
		print("looks good!")
		continue

	n_tabs = 4
	for s in spaces:
		l_s = len(s) - 1
		n_tabs = 4 if l_s % 2 == l_s % 4 == 0 else 2
		if n_tabs == 2:
			break

	for s in spaces:
		l_s = len(s) - 1
		tabs = "\n" + "\t" * (l_s // n_tabs)
		contents = contents.replace(s, tabs, 1)
	
	with open(f, "w") as file:
		file.write(contents)
	
	print("fixed")
