import os
import sys


def run(argv):
	if argv!=2:
		print("Usage : %s rootdir casename" %argv[0])
		exit(1)
	rootdir = argv[1]
	casename = argv[2]
	os.mkdir(roodir + "/" +casename)

if __name__=="__main__":
	run(sys.argv)

