#! /usr/bin/env python2

import sys
import urllib2

url = sys.argv[1]

file_name = url.split('/')[-1]
u = urllib2.urlopen(url)
f = open(file_name, 'w')
meta = u.info()
mega = 1024*1024.
file_size = int(meta.getheaders("Content-Length")[0]) / mega
#print "Downloading: %s Mb: %s" % (file_name, file_size)

file_size_dl = 0
block_sz = 8192
while True:
    buffer = u.read(block_sz)
    if not buffer:
        break
    file_size_dl += len(buffer) / mega
    f.write(buffer)
    status = file_name[:36].ljust(40) + "%7.2f Mb  [%3.2f%%]" % 
            (file_size_dl, file_size_dl * 100. / file_size)
    #status = status + chr(8)*(len(status)+1)
    print status,

f.close()
