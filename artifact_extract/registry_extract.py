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
	SAM_path = "Windows/System32/Config/SAM"
	SOFTWARE_path = "Windows/System32/Config/SOFTWARE"
	SECURITY_path = "Windows/System32/Config/SECURITY"
	SYSTEM_path = "Windows/System32/Config/SYSTEM"

	SAM = file.get_fileinfo(SAM_path,image_dir, casename)
	SOFTWARE=file.get_fileinfo(SOFTWARE_path,image_dir, casename)
	SECURITY=file.get_fileinfo(SECURITY_path, image_dir, casename)
	SYSTEM=file.get_fileinfo(SYSTEM_path, image_dir, casename)

	command = "extractdata -i "+argv[1]+"/"+casename+"/"+disk_image+" -o 0 -q "+str(SAM[0])+" -e "+argv[1]+"/"+casename+"/"+image_dir+"/registry/"+SAM[1]
	mftparse.run(command.split(" "))
	command = "extractdata -i "+argv[1]+"/"+casename+"/"+disk_image+" -o 0 -q "+str(SOFTWARE[0])+" -e "+argv[1]+"/"+casename+"/"+image_dir+"/registry/"+SOFTWARE[1]
	mftparse.run(command.split(" "))
	command = "extractdata -i "+argv[1]+"/"+casename+"/"+disk_image+" -o 0 -q "+str(SECURITY[0])+" -e "+argv[1]+"/"+casename+"/"+image_dir+"/registry/"+SECURITY[1]
	mftparse.run(command.split(" "))
	command = "extractdata -i "+argv[1]+"/"+casename+"/"+disk_image+" -o 0 -q "+str(SYSTEM[0])+" -e "+argv[1]+"/"+casename+"/"+image_dir+"/registry/"+SYSTEM[1]
	mftparse.run(command.split(" "))

	for user_inum, user in Userlist:
		NTUSER_path="Users/"+user+"/NTUSER.DAT"
		NTUSER = file.get_fileinfo(NTUSER_path, image_dir, casename)
		command = "extractdata -i "+argv[1]+"/"+casename+"/"+disk_image+" -o 0 -q "+str(NTUSER[0])+" -e "+argv[1]+"/"+casename+"/"+image_dir+"/registry/"+user+"_"+NTUSER[1]
		mftparse.run(command.split(" "))

def run(argv):
	if check_argument(argv) :
		exit(1)
	userlist=user_extract.user_info(argv)
	extract_artifact(argv,userlist)

if __name__ == "__main__":
	run(sys.argv)
