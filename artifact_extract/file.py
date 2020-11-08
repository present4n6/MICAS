import os
import sys
import csv
import MySQLdb

INUM=0
F_NAME=35
PARENTS=36


def check_argument(argv):
        if len(argv)!=3:
                print("Error")
                print("Usage : %s filelocation imagename casename" %argv[0])
                return True
        return False

def location_parse(location):
	path = location.split("/")
	return path

def get_dirinfo(location ,imagename, casename):
	path = location_parse(location)
	db = MySQLdb.connect(host="192.168.4.188",
				user="hadoopuser",
				password="Hadoopuser1!",
				db=casename,charset='utf8')
	cur = db.cursor()
	inum = 5
	for file in path:
		cur.execute("select inum from "+imagename+"_mftinfo where `FN pdfme`=%d and `FN name`='%s'" %(inum, file))
		try : inum = cur.fetchone()[0]
		except : return None
	cur.execute("select inum,`FN name`,directory from "+imagename+"_mftinfo where `FN pdfme`=%d" %(inum))
	return cur.fetchall()

def get_fileinfo(location, imagename, casename):

	path = location_parse(location)
	print(path)
	db = MySQLdb.connect(host="192.168.4.188",
				user="hadoopuser",
				password="Hadoopuser1!",
				db=casename, charset='utf8')
	cur = db.cursor()
	inum = 5
	for file in path:
		cur.execute("select inum from "+imagename+"_mftinfo where `FN pdfme`=%d and `FN name`='%s'" %(inum, file))
		try :
			inum = cur.fetchone()[0]
		except :
			return None
	f_info=[inum, path[-1]]
	return f_info

def run(argv):
        get_fileinfo(argv)

if __name__ == "__main__":
	if check_argument(sys.argv) :
		exit(1)
	run(sys.argv[1], sys.argv[2])
