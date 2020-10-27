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
                print("Usage :  root casename Imagefile")
                return True
        return False

def extract_artifact(argv):
	casename = argv[2]
	disk_image=argv[3]
	image_dir = argv[3].split(".")[0]

	db = MySQLdb.connect(host="192.168.4.188",
				user="hadoopuser",
				password="Hadoopuser1!",
				db=casename, charset='utf8')
	cur = db.cursor()

	cur.execute("SELECT * FROM "+image_dir+"_mftinfo WHERE `FN name`  LIKE '%.ost' OR `FN name` LIKE '%.eml' OR `FN name` LIKE '%.pst';")
	for row in cur.fetchall():
		print(row)
		print(str(row[INUM]) + " " + row[F_NAME])
		command = "extractdata -i" + " " + argv[1] +"/" + casename + "/"+ disk_image + " " + "-o 0 -q" + " " + str(row[INUM]) + " " + "-e" + " " +argv[1]+"/"+casename+"/"+image_dir+"/email/" + row[F_NAME].replace(" ", "")
		mftparse.run(command.split(" "))

def run(argv):
        if check_argument(argv) :
                exit(1)
        extract_artifact(argv)

if __name__ == "__main__":
	run(sys.argv)
