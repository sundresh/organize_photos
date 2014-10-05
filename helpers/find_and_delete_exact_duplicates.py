#!/usr/bin/env python
#
# Script to find and (optionally) delete exact duplicate photos found in the
# same directory.
#
# Usage: ./find_and_delete_exact_duplicates.py ~/Photos
#

from collections import defaultdict
import os, sys

DELETE = False
AUTO_DELETE = False

def is_duplicate(f1, f2):
	return open(f1).read() == open(f2).read()

num_sets = 0
num_bytes = 0
num_sets_deleted = 0
num_bytes_deleted = 0

for (dirpath, dirnames, filenames) in os.walk(sys.argv[1]):
	size_to_filenames = defaultdict(lambda: set())
	for filename in filenames:
		size = os.stat(os.path.join(dirpath, filename)).st_size
		size_to_filenames[size].add(filename)

	for (size, filenames) in size_to_filenames.items():
		filenames = list(f for f in filenames if not f.startswith('DELETE_'))
		true_duplicate_filenames = [filenames[0]]
		for f in filenames[1:]:
			if is_duplicate(os.path.join(dirpath, filenames[0]), os.path.join(dirpath, f)) \
			and not f.startswith('DELETE_'):
				true_duplicate_filenames.append(f)
		filenames = true_duplicate_filenames
		
		if len(filenames) > 1:
			print '%s: %s' % (dirpath, ', '.join("'%s'" % f for f in filenames))
			num_sets += 1
			num_bytes += size * (len(filenames) - 1)

			if DELETE:
				if len([f for f in filenames if f.startswith('IMG_') or f.startsiwth('DSC_')]) == 1:
					if not AUTO_DELETE:
						os.system('open ' + ' '.join("'%s'" % os.path.join(dirpath, f) for f in filenames))
					files_to_delete = [f for f in filenames if not (f.startswith('IMG_') or f.startswith('DSC_'))]
					print [os.path.join(dirpath, f) for f in files_to_delete]
					if AUTO_DELETE or (raw_input('Delete? ') == 'Y'):
						for f in files_to_delete:
							cmd = "mv '%s' '%s'" % (os.path.join(dirpath, f), os.path.join(dirpath, 'DELETE_' + f))
							print cmd
							os.system(cmd)
							num_sets_deleted += 1
							num_bytes_deleted += size * (len(filenames) - 1)
					print

print {'num_sets': num_sets, 'num_bytes': num_bytes, 'num_sets_deleted': num_sets_deleted, 'num_bytes_deleted': num_bytes_deleted}
