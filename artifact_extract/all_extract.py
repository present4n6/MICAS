import os
import sys
import csv
sys.path.insert(1, '/home/hadoopuser/python_code/ntfs_parse/')
import mftparse
import MySQLdb
import file
import user_extract
import email_extract
import evtx_extract
import fslog_extract
import prefetch_extract
import recycle_extract
import registry_extract
import webartifact_extract

INUM=0
F_NAME=35
PARENTS=36


def check_argument(argv):
        if len(argv)!=4:
                print("Error")
                print("Usage : rootdir casename Imagefile")
                return True
        return False

def extract_artifact(argv):
	rootdir=argv[1]
	casename=argv[2]
	disk_image=argv[3]
	image_dir= disk_image.split(".")[0]

	user_extract.extract_artifact(roodir, casename, disk_image)
	email_extract.extract_artifact(roodir, casename, disk_image)
	evtx_extract.extract_artifact(roodir, casename, disk_image)
	fslog_extract.extract_artifact(rootdir, casename, disk_image)
	prefetch_extract.extract_artifact(rootdir, casename, disk_image)
	recycle_extract.extract_artifact(rootdir, casename, disk_image)
	registry_extract.extract_artifact(rootdir, casename, disk_image)
	webartifact_extract.extract_artifact(rootdir, casename, disk_image)


def run(argv):
	if check_argument(argv) :
		exit(1)
	extract_artifact(argv)

if __name__ == "__main__":
	run(sys.argv)
