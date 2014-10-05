#!/usr/bin/env python

from collections import defaultdict
import os, sys

def is_duplicate(f1, f2):
	return open(f1).read() == open(f2).read()

size_to_filepaths = defaultdict(lambda: set())

for (dirpath, dirnames, filenames) in os.walk(sys.argv[1]):
	for filename in filenames:
		filepath = os.path.join(dirpath, filename)
		size = os.stat(filepath).st_size
		size_to_filepaths[size].add(filepath)


num_sets = 0
num_bytes = 0

for (size, filepaths) in size_to_filepaths.items():
	filepaths = list(filepaths)
	true_duplicate_filepaths = [filepaths[0]]
	for f in filepaths[1:]:
		if is_duplicate(os.path.join(dirpath, filepaths[0]), os.path.join(dirpath, f)):
			true_duplicate_filepaths.append(f)
	filepaths = true_duplicate_filepaths
	if len(filepaths) > 1:
		print filepaths
		num_sets += 1
		num_bytes += (len(filepaths) - 1) * size

print (num_sets, num_bytes)
