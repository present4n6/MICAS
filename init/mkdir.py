import os
import sys


def argcheck(argv):
	if len(argv)!=4:
		print("Usage : root, casename, imagename")
		exit(1) 

def run(argv):

	argcheck(argv)

	try:
		os.mkdir("%s/%s" %(argv[1], argv[2]))
	except:
		pass

	os.mkdir("%s/%s/%s" %(argv[1], argv[2], argv[3]))
	os.mkdir("%s/%s/%s/user" %(argv[1], argv[2], argv[3]))
	os.mkdir("%s/%s/%s/email" %(argv[1], argv[2], argv[3]))
	os.mkdir("%s/%s/%s/eventlog" %(argv[1], argv[2], argv[3]))
	os.mkdir("%s/%s/%s/fslog" %(argv[1], argv[2], argv[3]))
	os.mkdir("%s/%s/%s/registry" %(argv[1], argv[2], argv[3]))
	os.mkdir("%s/%s/%s/prefetch" %(argv[1], argv[2], argv[3]))
	os.mkdir("%s/%s/%s/recycle" %(argv[1], argv[2], argv[3]))

if __name__=="__main__":
	run(sys.argv)
