#
# organize_photos.py: (C) 2011-2022 Sameer Sundresh. No warranty.
#
# exif_cache.py is a helper for organize_photos.py
#
# It maintains a cache file exif_cache.json in the source directory that
# keeps track of which files have already been copied out of that source
# directory, including where they were copied and their size and filename.
#
# Note that this cache has only been tested in the case where there is
# just one destination directory. If you plan to use this script with the
# same SD card on multiple computers (for example), you should check to
# make sure that it actually works correctly!
#

import json, logging, os, os.path, time

_TIME_PRINT_FORMAT = '%Y-%m-%d %H:%M:%S UTC'
_TIME_PARSE_FORMAT = '%Y-%m-%d %H:%M:%S %Z'

def format_time(timestamp):
    return time.strftime(_TIME_PRINT_FORMAT, time.gmtime(timestamp))

def parse_time(time_string):
    return (time.mktime(time.strptime(time_string, _TIME_PARSE_FORMAT)) - time.timezone)

def is_direct_rel_path(path):
    if path[0] == '/':
        return False
    path = os.path.join('/', path)
    return path == os.path.abspath(path)

def backup_file(file_path):
    if os.path.lexists(file_path):
        i = 0
        while True:
            i += 1
            bak_path = '%s.bak%i' % (file_path, i)
            if not os.path.lexists(bak_path):
                os.rename(file_path, bak_path)
                return bak_path

def time_close_enough(t0, t1, is_src=False):
    if is_src:
        return -10 <= ((t0 - t1) - round((t0 - t1) / 3600.0) * 3600) <= 10
    else:
        return -10 <= (t0 - t1) <= 10

class ExifCache(object):
    def __init__(self, src_dir_path, dest_dir_path, autosave_interval=0):
        self.src_dir_path = src_dir_path
        self.dest_dir_path = dest_dir_path
        self.autosave_interval = autosave_interval
        self._adds_since_last_save = 0
        print('Loading EXIF cache...')
        self.data = self._load()

    def _load(self):
        # Read the JSON EXIF cache data
        exif_cache_path = os.path.join(self.src_dir_path, 'exif_cache.json')
        if os.path.lexists(exif_cache_path):
            assert not os.path.islink(exif_cache_path)
            with open(exif_cache_path, 'r') as f:
                exif_cache_data = json.load(f)
        else:
            exif_cache_data = { }

        # Check that the EXIF cache data is well-formed,
        # and parse all the time strings as timestamps.
        data = { }
        for entry in exif_cache_data.items():
            try:
                (src_img_path, [dest_img_path, size, time_string]) = entry
                assert is_direct_rel_path(src_img_path)
                assert is_direct_rel_path(dest_img_path)
                assert (type(size) == int) and (size >= 0)
                timestamp = parse_time(time_string)
                data[src_img_path] = (dest_img_path, size, timestamp)
            except:
                logging.error('Could not decode EXIF cache entry %s' % repr(entry))
        return data

    def save(self):
        if self._adds_since_last_save == 0:
            return

        print('Saving EXIF cache...')

        # Check that the EXIF cache data is well-formed,
        # and format all the timestamps as time string.
        exif_cache_data = { }
        for (src_img_path, (dest_img_path, size, timestamp)) in self.data.items():
            assert is_direct_rel_path(src_img_path)
            assert is_direct_rel_path(dest_img_path)
            assert (type(size) == int) and (size >= 0)
            time_string = format_time(timestamp)
            exif_cache_data[src_img_path] = (dest_img_path, size, time_string)

        # Backup the old JSON EXIF cache data and write the new data
        exif_cache_path = os.path.join(self.src_dir_path, 'exif_cache.json')
        backup_file_path = backup_file(exif_cache_path)
        with open(exif_cache_path, 'w') as f:
            json.dump(exif_cache_data, f)

        # Check that the data was written correctly, and if so, remove the backup
        if self._load() == self.data:
            if backup_file_path:
                os.remove(backup_file_path)
        else:
            logging.error('Error saving EXIF cache')
            # Should raise an exception...

        self._adds_since_last_save = 0

    def check(self, src_img_path):
        try:
            # Get cache entry
            rel_src_img_path = os.path.relpath(src_img_path, self.src_dir_path)
            (rel_dest_img_path, size, timestamp) = self.data.get(rel_src_img_path)
            # Absolute dest_img_path
            dest_img_path = os.path.join(self.dest_dir_path, rel_dest_img_path)
            # Check file paths exist
            assert os.path.exists(src_img_path) and os.path.exists(dest_img_path)
            # Check file sizes match
            assert os.path.getsize(src_img_path) == size == os.path.getsize(dest_img_path)
            # Check file mtimes match
            #assert time_close_enough(os.path.getmtime(src_img_path), timestamp, is_src=True)
            assert time_close_enough(os.path.getmtime(dest_img_path), timestamp)
            return True
        except:
            return False

    def add(self, src_img_path, dest_img_path):
        # Check file paths exist
        assert os.path.exists(src_img_path) and os.path.exists(dest_img_path)
        rel_src_img_path = os.path.relpath(src_img_path, self.src_dir_path)
        rel_dest_img_path = os.path.relpath(dest_img_path, self.dest_dir_path)
        # Check file sizes match
        size = os.path.getsize(src_img_path)
        assert os.path.getsize(dest_img_path) == size
        # Check file mtimes match
        timestamp = os.path.getmtime(src_img_path)
        #assert time_close_enough(os.path.getmtime(dest_img_path), timestamp, is_src=True)
        # Write to cache
        self.data[rel_src_img_path] = (rel_dest_img_path, size, int(timestamp))

        # Autosave
        self._adds_since_last_save += 1
        if self.autosave_interval > 0 and self._adds_since_last_save >= self.autosave_interval:
            self.save()
