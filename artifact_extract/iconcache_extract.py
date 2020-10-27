import os
import sys
import csv
sys.path.insert(1, '../ntfs_parse/')
import mftparse
import MySQLdb
import file
import user_extract

INUM=0
F_NAME=35
PARENTS=36


def check_argument(argv):
        if len(argv)!=4:
                print("Error")
                print("Usage : %s root casename Imagefile" %argv[0])
                return True
        return False

def extract_artifact(argv, Userlist):
	disk_image = argv[3]
	casename=argv[2]
	image_dir= disk_image.split(".")[0]
	for user_inum, user in Userlist:
		icon_path = "Users/"+user+"/AppData/Local/IconCache.db"
		icon = file.get_fileinfo(icon_path,image_dir, casename)
		command = "extractdata -i" + " " + argv[1]+"/"+casename+"/"+disk_image + " " + "-o 0 -q" + " " + str(icon[0]) + " " + "-e" + " " + argv[1] +"/" +casename + "/" +image_dir+ "/user/"+user+"/iconcache/" + icon[1].replace(" ","")
		mftparse.run(command.split(" "))

def run(argv):
	if check_argument(argv) :
		exit(1)
	userlist=user_extract.user_info(argv)
	extract_artifact(argv,userlist)

if __name__ == "__main__":
	run(sys.argv)
