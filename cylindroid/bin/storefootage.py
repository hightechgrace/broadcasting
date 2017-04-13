#!/usr/bin/env python

import os, sys, time, shutil

if len(sys.argv) < 3:
    print "usage: %s source_files... target_directory" % sys.argv[0]
    sys.exit(1)

source_files = sys.argv[1:-1]
target_directory = sys.argv[-1]

if not os.path.isdir(target_directory):
    print "not a directory: %s" % target_directory
    sys.exit(1)

ops = []
cleanup_queue = []

def process_file(src_file):
    if src_file[0] == '.':
        return
    if os.path.basename(src_file) == 'old':
        return

    if os.path.isdir(src_file):
        for f in os.listdir(src_file):
            process_file(os.path.join(src_file, f))
        return

    if not os.path.isfile(src_file):
        return
    if os.path.splitext(src_file)[1].lower() not in ('.mov', '.m4a', '.mp4', '.m4v', '.aif', '.wav'):
        return
    if src_file.find('temp-') >= 0:
        return
    if os.stat(src_file).st_size < 1e6:
        return

    ctime = time.localtime(os.stat(src_file).st_ctime)
    dir_label = time.strftime('%Y%m%d', ctime)
    file_label = time.strftime('%H%M%S_', ctime)

    dest_dir = os.path.join(target_directory, dir_label)
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)

    dest_file = os.path.join(dest_dir, file_label + os.path.basename(src_file))

    if not os.path.isfile(dest_file):
        ops.append((src_file, dest_file))
        print('preparing move: %s -> %s' % (src_file, dest_file))

def atomic_move(src_file, dest_file):
    temp_file = dest_file + '-temp'
    old_file = src_file + '-old'
    shutil.copy2(src_file, temp_file)
    os.rename(temp_file, dest_file)
    if os.stat(src_file).st_size == os.stat(dest_file).st_size:
        try:
            os.rename(src_file, old_file)
            cleanup_queue.append(old_file)
            print('finished: %s -> %s' % (src_file, dest_file))
        except Exception, e:
            print('ERROR while cleaning up, leaving file. Tried to rename %s to %s' % (src_file, old_file))
    else:
        print('MISMATCH, changed while copying? leaving file. %s' % src_file)

for src_file in source_files:
    process_file(src_file)

for src_file, dest_file in ops:
    atomic_move(src_file, dest_file)

for old_file in cleanup_queue:
    try:
    	os.unlink(old_file)
    except OSError:
    	pass
