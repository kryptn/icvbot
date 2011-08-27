#/usr/bin/python
import os, sys
status = 9

while status == 9:
   status = int(os.system("python icvbot.py "+' '.join(sys.argv[1:])) / 256)
   print "Controller: %d" % (status)