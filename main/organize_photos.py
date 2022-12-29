#!/usr/bin/env python3
#
# organize_photos.py: (C) 2011-2022 Sameer Sundresh. No warranty.
#
# organize_photos.py is a simple system to organize your camera photos by
# date. It is primarily intended for copying photos off of an SD card
# (without removing them from the SD card), but also works for copying
# photos out of other directories, of course.
#
# We try to use the EXIF photo time taken timestamp, but fall back to file
# modified timestamp if necessary. As a special case, we are also able to
# parse Dropbox Camera Uploads filenames as timestamps.
#

try:
  import exifread, PIL.Image
  USE_LIBRARIES = True
except:
  USE_LIBRARIES = False

import os, os.path, re, shutil, sys, time, traceback
from exif_cache import ExifCache

PHOTOS_ROOT = os.path.expanduser('~/Photos')
os.umask(0o027)
FILE_PERMISSIONS = 0o440


def add_photos(src_dir_path):
    exif_cache = ExifCache(src_dir_path, PHOTOS_ROOT, autosave_interval=25)
    print('Scanning files...')
    for (dirpath, dirnames, filenames) in os.walk(src_dir_path):
        for filename in filenames:
            src_path = os.path.join(dirpath, filename)
            upper = filename.upper()
            extension = upper[upper.rindex('.')+1:] if ('.' in upper) else ''
            if extension in ['AAE', 'HEIC', 'JPG', 'JPEG', 'AVI', 'MOV', 'MP4', 'PNG', 'GIF', 'TIF', 'TIFF', 'WEBP']:
                try:
                    if not exif_cache.check(src_path):
                        dest_path = add_photo(src_path)
                        exif_cache.add(src_path, dest_path)
                except Exception as e:
                    traceback.print_exc()
                    sys.stderr.write('Skipping file %s due to exception %s\n' % (src_path, e))
            elif extension not in ['CTG', 'DS_Store', 'THM', 'json']: # explicitly ignored extensions
                sys.stderr.write('Skipping non-image file %s\n' % src_path)
    exif_cache.save()

def add_photo(src_path):
    """ Add a photo to our photo archive, organized by date taken.  Skips
    duplicates, but prevents different photos with the same filename from
    conflicting. """
    photo_name = get_photo_name(src_path)
    photo_date = get_photo_taken_date(src_path)
    date_dir   = get_dir_for_date(photo_date)
    roll = None
    dupe = False
    for i in range(0, 999): # XXX
        roll = alphabetic(i)
        dest_path = os.path.join(date_dir, roll, photo_name)
        if not os.path.exists(dest_path):
            break
        if is_duplicate(src_path, photo_date, dest_path):
            dupe = True
            break
    if dupe:
        sys.stderr.write('Skipping duplicate %s =/=> %s\n' % (src_path, dest_path))
    else:
        sys.stdout.write('%s ==> %s\n' % (src_path, dest_path))
        dest_dir = os.path.dirname(dest_path)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        shutil.copyfile(src_path, dest_path)
        t = time.mktime(photo_date)
        os.utime(dest_path, (t, t))
        os.chmod(dest_path, FILE_PERMISSIONS)
    return dest_path

def get_photo_name(src_path):
    """ Gets a photo's name based on its path, normalizing away iPhoto name modifications. """
    photo_name = os.path.basename(src_path)
    #matches = re.match('^(?P<basename>[A-Za-z]+_[0-9]+)_[0-9]+\.(?P<extension>[A-Za-z]+)$', photo_name)
    matches = re.match('^(?P<basename>[A-Za-z]+[_0-9]+)\.(?P<extension>[A-Za-z]+)$', photo_name)
    if matches:
        photo_name = '%s.%s' % (matches.group('basename'), matches.group('extension'))
    return photo_name

DATE_TIME_ORIGINAL = 0x9003
if USE_LIBRARIES:
    assert exifread.EXIF_TAGS[DATE_TIME_ORIGINAL][0] == 'DateTimeOriginal'
DROPBOX_FILE_NAME_REGEX = re.compile('^([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}\.[0-9]{2}\.[0-9]{2})')
DROPBOX_FILE_NAME_STRPTIME = '%Y-%m-%d %H.%M.%S'

def get_photo_taken_date_from_filesystem(src_path):
    """ Gets a struct_time representing the time and date the photo file was created. """
    sys.stderr.write('Warning: using filesystem date for file %s\n' % src_path)
    s = os.stat(src_path)
    return time.localtime(min(s.st_ctime, s.st_mtime))

def get_photo_taken_date_from_photo_metadata(src_path):
    """ Gets a struct_time representing the time and date the photo was taken. """
    # Both exifread and PIL.Image seem to have incomplete EXIF support (i.e.,
    # they don't work with some images), so try both and hope for the best.
    try:
        f = open(src_path, 'rb')
        tags = exifread.process_file(f, details=False, stop_tag='DateTimeOriginal')
        f.close()
        date_time_original = str(tags['EXIF DateTimeOriginal'])
        return time.strptime(date_time_original, '%Y:%m:%d %H:%M:%S')
    except:
        try:
            date_time_original = image.open(src_path)._getexif().get(DATE_TIME_ORIGINAL)
            return time.strptime(date_time_original, '%Y:%m:%d %H:%M:%S')
        except:
            print("DROPBOX_FILE_NAME_REGEX.match('%s')" % (os.path.basename(src_path),))
            m = DROPBOX_FILE_NAME_REGEX.match(os.path.basename(src_path))
            if m is not None:
                return time.strptime(m.group(1), DROPBOX_FILE_NAME_STRPTIME)
            else:
                return get_photo_taken_date_from_filesystem(src_path)

def get_photo_taken_date(src_path):
    if USE_LIBRARIES:
        return get_photo_taken_date_from_photo_metadata(src_path)
    else:
        return get_photo_taken_date_from_filesystem(src_path)

def get_dir_for_date(photo_date):
    """ Construct the directory path for photos for a particular date. """
    return os.path.join(PHOTOS_ROOT, '%d' % photo_date.tm_year, '%02d' % photo_date.tm_mon, '%02d' % photo_date.tm_mday)

def is_duplicate(photo_path1, photo_date1, photo_path2):
    """ Determine whether two photos are exactly the same.  Returns True/False. """
    stat1 = os.stat(photo_path1)
    stat2 = os.stat(photo_path2)
    if stat1.st_size != stat2.st_size:
        return False
    if USE_LIBRARIES and photo_date1 != get_photo_taken_date(photo_path2):
        return False
    return same_contents(photo_path1, photo_path2)

def same_contents(path1, path2):
    """ Determine whether two files contain the same exact contents.  Returns True/False. """
    f1 = open(path1, 'rb')
    f2 = open(path2, 'rb')
    try:
        return f1.read() == f2.read()
    finally:
        f1.close()
        f2.close()

def alphabetic(num):
    """ Creates alphabetic encodings of numbers like A, B, C, ... Z, AA, AB, ... AZ, BA, ..., ZZ, AAA, ... """
    letters = []
    while num >= 0:
        letters.append(chr(ord('A') + (num % 26)))
        num = (num / 26) - 1
    letters.reverse()
    return ''.join(letters)

if __name__ == '__main__':
    add_photos(sys.argv[1])
