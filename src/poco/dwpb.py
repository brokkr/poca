#! /usr/bin/env python2

import sys
import urllib2

url = sys.argv[1]

def progress_download(url):
    # get metainformation and open remote and local file, respectively
    file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name, 'w')
    meta = u.info()
    mega = 1024*1024.
    file_size = int(meta.getheaders("Content-Length")[0]) / mega
    file_size_dl = 0
    block_sz = 65536
    
    # download chunks of block_size until there is no more to read
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer) / mega
        f.write(buffer)
        status = file_name[:36].ljust(40) + "%7.2f Mb  [%3.2f%%]" % \
            (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,
    
    # close file and print a newline
    f.close()
    print '\n'

progress_download(url)

