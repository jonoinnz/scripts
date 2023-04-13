#!/usr/bin/env python3

'''
A script to recursively compare two directories (including file size and file hash changes)
Usage: python3 compare_dirs.py DIR1 DIR2
'''

import os, sys, hashlib, unicodedata

COMPARE_FILES = True            # should file sizes be compared if their names are the same?
MD5 = True                      # should file hash sums be compared if their names and sizes are the same?
COLORIZE = True                # colorization for bash (only Linux & Unix)
BUFF_SIZE = 1<<26               # 64 MB buffer

def md5sum(fn):
    hasher = hashlib.md5()
    with open(fn, "rb") as f:
        chunk = f.read(BUFF_SIZE)
        while chunk:
            hasher.update(chunk)
            chunk = f.read(BUFF_SIZE)
    return hasher.hexdigest()

WHITE, RED, GREEN = 15, 196, 46
fg = lambda text, color: "\33[38;5;" + str(color) + "m" + text + "\33[0m"

# Some SSDs change bytecodes of Unicode names from NFC to NFD; need to normalize
NFD = lambda x: unicodedata.normalize('NFD', x)

def compare_dirs(d1: "old directory name", d2: "new directory name"):
    def print_local(a, msg):
        text = '{} {} {}'.format('DIR ' if a[2] else 'FILE', a[1], msg)
        if COLORIZE:
            color = {'added': GREEN, 'removed': RED}.get(msg, WHITE)
            print(fg(text, color))
        else:
            print(text)
    # Ensure validity
    for d in [d1,d2]:
        if not os.path.isdir(d):
            raise ValueError("not a directory: " + d)
    # Get relative path
    l1 = [(NFD(fn), os.path.join(d1, fn)) for fn in os.listdir(d1)]
    l2 = [(NFD(fn), os.path.join(d2, fn)) for fn in os.listdir(d2)]
    # Determine type: directory or file?
    l1 = sorted([(fn, pth, os.path.isdir(pth)) for fn, pth in l1])
    l2 = sorted([(fn, pth, os.path.isdir(pth)) for fn, pth in l2])
    i1 = i2 = 0
    cnt = 0
    common_dirs = []
    while i1<len(l1) and i2<len(l2):
        if l1[i1][0] == l2[i2][0]:      # same name
            if l1[i1][2] == l2[i2][2]:  # same type
                if l1[i1][2]:
                    # Pair of directories -> remember the name for recursion
                    common_dirs.append((l1[i1][1], l2[i2][1]))
                elif COMPARE_FILES:
                    # Pair of files -> compare their sizes
                    size1 = os.stat(l1[i1][1]).st_size
                    size2 = os.stat(l2[i2][1]).st_size
                    if size1!=size2:
                        print_local(l1[i1],'size changed: {:d} -> {:d}'.format(size1, size2))
                    elif MD5:
                        # Sizes are the same -> compare MD5 hashes
                        if md5sum(l1[i1][1])!=md5sum(l2[i2][1]):
                            print_local(l1[i1],'hash changed')
            else:
                print_local(l1[i1],'type changed')
            i1 += 1
            i2 += 1
        elif l1[i1][0]<l2[i2][0]:
            print_local(l1[i1],'removed')
            i1 += 1
        elif l1[i1][0]>l2[i2][0]:
            print_local(l2[i2],'added')
            i2 += 1
        cnt += 1
    while i1<len(l1):
        print_local(l1[i1],'removed')
        i1 += 1
        cnt += 1
    while i2<len(l2):
        print_local(l2[i2],'added')
        i2 += 1
        cnt += 1
    # Compare subfolders recursively
    for sdir1,sdir2 in common_dirs:
        cnt += compare_dirs(sdir1, sdir2)
    return cnt

if __name__=='__main__':
    print ('Comparing files {}abled'.format('en' if COMPARE_FILES else 'dis'))
    print ('MD5 checking {}abled'.format('en' if MD5 else 'dis'))
    print ('Colorization {}abled'.format('en' if COLORIZE else 'dis'))
    print (compare_dirs(sys.argv[1], sys.argv[2]), 'items compared')
