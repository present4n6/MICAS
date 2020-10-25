import os
import sys
import csv
sys.path.insert(1, '../ntfs_parse/')
import mftparse
import MySQLdb

INUM=0
F_NAME=35
PARENTS=36


def check_argument(argv):
        if len(argv)!=4:
                print("Error")
                print("Usage : %s root casename Imagefile" %argv[0])
                return True
        return False

def extract_artifact(argv):
	dbname=argv[2]
	casename=argv[2]
	db = MySQLdb.connect(host="192.168.4.188",
				user="hadoopuser",
				password="Hadoopuser1!",
				db=dbname, charset='utf8')
	cur = db.cursor()
	cur.execute("SELECT * FROM mftinfo WHERE `FN name`  LIKE '%.pf'")
	disk_image= argv[3]
	image_dir = argv[3].split(".")[0]

	for row in cur.fetchall():
		print(row)
		print(str(row[INUM]) + " " + row[F_NAME])
		command = "extractdata -i" + " " + argv[1]+ "/" +casename+"/"+ disk_image + " " + "-o 0 -q" + " " + str(row[INUM]) + " " + "-e" + " " + argv[1]+"/"+argv[2]+"/"+image_dir+"/prefetch/" + row[F_NAME].replace(" ", "")
		mftparse.run(command.split(" "))

def run(argv):
        if check_argument(argv) :
                exit(1)
        extract_artifact(argv)

if __name__ == "__main__":
	run(sys.argv)
