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
	dbname=argv[2]
	disk_image = argv[3]
	casename=argv[2]
	image_dir= disk_image.split(".")[0]
	for user_inum, user in Userlist:
		link_path = "Users/"+user+"/AppData/Roaming/Microsoft/Windows/Recent"
		link_dir = file.get_dirinfo(link_path,image_dir,casename)
		for files in link_dir :
			if files[2]=="False" :
				command = "extractdata -i" + " " + argv[1]+"/"+casename+"/"+disk_image + " " + "-o 0 -q" + " " + str(files[0]) + " " + "-e" + " " + argv[1] +"/" +casename + "/" +image_dir+ "/user/"+user+"/linkfile/" + files[1].replace(" ","")
				mftparse.run(command.split(" "))

def run(argv):
	if check_argument(argv) :
		exit(1)
	userlist=user_extract.user_info(argv)
	extract_artifact(argv,userlist)

if __name__ == "__main__":
	run(sys.argv)
