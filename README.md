organize_photos
===============

Python script to organize photos by date

The main organize_photos.py is in "main"; other helper programs for use
in re-organizing disorganized photos is in "helpers".

Please see comments in organize_photos.py and exif_cache.py

As mentioned in the LICENSE file, this software comes without warranty.
Audit the code yourself and use at your own risk. Backup your photos often
to several drives in different locations to keep them safe.

Getting started:

OPTIONAL: Create a python virtual environment and install the "exifread"
and "pillow" packages (if you don't do this, photos will be organized by
the earlier of their ctime and mtime filesystem timestamps rather than
based on metadata within the files):

```
virtualenv ve
source ve/bin/activate
pip install exifread pillow
```

Usage:

```
source ve/bin/activate  # OPTIONAL: to use libraries installed above
./organize_photos.py /path/to/source/photos/dir
```

Be sure to test this out with a test source directory and test destination
directory. Copy a few photos into a new directory as the test source, and
create a new directory as the test destination. Again, audit the code yourself
and use at your own risk!
