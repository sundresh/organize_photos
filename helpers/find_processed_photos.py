#!/usr/bin/env python

from collections import defaultdict
import exifread, os, PIL.Image, sys

DATE_TIME = 'Image DateTime'
DATE_TIME_ORIGINAL = 'EXIF DateTimeOriginal'
SOFTWARE = 'Image Software'

num_bytes = 0

for (dirpath, dirnames, filenames) in os.walk(sys.argv[1]):
	for filename in filenames:
		filepath = os.path.join(dirpath, filename)
		upper = filename.upper()
		extension = upper[upper.rindex('.')+1:] if ('.' in upper) else ''
		if extension in ['JPG', 'JPEG', 'AVI', 'MOV', 'MP4', 'PNG', 'GIF', 'TIF', 'TIFF']:
			f = open(filepath, 'rb')
			tags = exifread.process_file(f, details=False)#, stop_tag='DateTimeOriginal')
			f.close()
			if DATE_TIME in tags and DATE_TIME_ORIGINAL in tags and SOFTWARE in tags:
				date_time_original = str(tags[DATE_TIME_ORIGINAL])
				date_time = str(tags[DATE_TIME])
				software = str(tags[SOFTWARE])
				if date_time_original != date_time and software == 'QuickTime 7.5':
					print '%s : %s vs. %s' % (filepath, date_time_original, date_time)
					num_bytes += os.stat(os.path.join(dirpath, filename)).st_size

print num_bytes
