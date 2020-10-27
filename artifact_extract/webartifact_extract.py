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
        if len(argv)!=3:
                print("Error")
                print("Usage : %s root casename Imagefile" %argv[0])
                return True
        return False

def extract_artifact(argv, Userlist):
	disk_image = argv[3]
	casename=argv[2]
	image_dir= disk_image.split(".")[0]
	for user_inum, user in Userlist:
		chome_cache = "Users/"+user+"/AppData/Local/Google/Chrome/User Data/Default/Cache"
		chrome_history = "Users/"+user+"/AppData/Local/Google/Chrome/User Data/Default/History"
		edge_history = "Users/"+user+"/AppData/Local/Microsoft/Edge/User Data/Default/History"
		ie_history = "Users/"+user+"/AppData/Local/Microsoft/Windows/WebCache/WebCacheV01.dat"

		cache=file.getfileinfo(chrome_cache,image_dir, casename)
		chrome = file.get_fileinfo(chrome_history,image_dir, casename)
		edge = file.get_fileinfo(edge_history,image_dir, casename)
		ie = file.get_fileinfo(ie_history,image_dir, casename)

		if cache :
			command = "extractdata -i "+argv[1]+"/"+casename+"/"+disk_image+" -o 0 -q "+str(cache[0])+" -e "+argv[1]+"/"+casename+"/"+image_dir+"/user/"+user+"web/chrome/cache/"+cache[1].replcae(" ", "")
			mftparse.run(command.split(" "))

		if chrome :
			command = "extractdata -i "+argv[1]+"/"+casename+"/"+disk_image+" -o 0 -q "+str(chrome[0])+" -e "+argv[1]+"/"+casename+"/"+image_dir+"/user/"+user+"web/chrome/history/"+chrome[1].replcae(" ", "")
			mftparse.run(command.split(" "))
		if edge:
			command = "extractdata -i" + " " + argv[1]+"/"+casename+"/"+disk_image + " " + "-o 0 -q" + " " + str(edge[0]) + " " + "-e" + " " + argv[1] +"/" +casename + "/" +image_dir+ "/user/"+user+"/web/edge/history/" + edge[1].replace(" ", "")
			mftparse.run(command.split(" "))
		if ie:
			command = "extractdata -i" + " " + argv[1]+"/"+casename+"/"+disk_image + " " + "-o 0 -q" + " " + str(ie[0]) + " " + "-e" + " " + argv[1] +"/" +casename + "/" +image_dir+ "/user/"+user+"/web/ie/history/" + ie[1].replace(" ", "")
			mftparse.run(command.split(" "))

def run(argv):
	if check_argument(argv) :
		exit(1)
	userlist=user_extract.user_info(argv)
	extract_artifact(argv,userlist)

if __name__ == "__main__":
	run(sys.argv)
