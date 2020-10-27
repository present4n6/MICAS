import os
import sys
import csv
sys.path.insert(1, '../ntfs_parse/')
import mftparse
import MySQLdb
import file

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
	disk_image = argv[3]
	casename=argv[2]
	image_dir= disk_image.split(".")[0]

	db=MySQLdb.connect(host="192.168.4.188",
				user="hadoopuser",
				password="Hadoopuser1!",
				db=dbname, charset='utf8')
	cur = db.cursor()
	cur.execute("select inum from "+image_dir+"_ mftinfo where `FN name`='$Recycle.Bin'")
	inum = cur.fetchall()[0][0]
	cur.execute("select * from "+image_dir+"_ mftinfo where `FN pdfme`="+str(inum))
	recycle_list= cur.fetchall()
	for row in recycle_list:
		os.mkdir("%s/%s/%s/%s/%s" %(argv[1], argv[2], image_dir,"recycle", row[F_NAME]))
		cur.execute("select inum, `FN name` from "+image_dir+"_ mftinfo where `FN pdfme`="+str(row[0]))
		for recycle in cur.fetchall():
			command = "extractdata -i "+argv[1]+"/"+casename+"/"+disk_image+" -o 0 -q "+str(recycle[0])+" -e "+argv[1]+"/"+casename+"/"+image_dir+"/recycle/"+row[F_NAME]+"/"+recycle[1]
			mftparse.run(command.split(" "))

def run(argv):
	if check_argument(argv) :
		exit(1)
	extract_artifact(argv)

if __name__ == "__main__":
	run(sys.argv)
