organize_photos
===============

Python script to organize photos by date

Please see comments in organize_photos.py and exif_cache.py

As mentioned in the LICENSE file, this software comes with warranty. Audit
the code yourself and use at your own risk. Backup your photos often to
several drives in different locations to keep them safe.

Getting started:

Created a python virtual environment and install the "exifread" and "pillow"
packages:

$ virtualenv ve
$ source ve/bin/activate
$ pip install exifread pillow

Usage:

$ source ve/bin/activate
$ ./organize_photos.py /path/to/source/photos/dir

Be sure to tests this out with a test source directory and test destination
directory. Copy a few photos into a new directory as the test source, and
create a new directory as the test destination. Again, audit the code yourself
and use at your own risk!
