import os
import sys
import MySQLdb

import webartifact_extract
import jumplist_extract
import linkfile_extract
import registry_extract
import iconcache_extract

INUM=0
F_NAME=35
PARENTS=36


def check_argument(argv):
        if len(argv)!=4:
                print("Error")
                print("Usage : %s rootdir casename Imagefile" %argv[0])
                return True
        return False

def user_info(argv):

	casename = argv[2]
	disk_image=argv[3]
	image_dir=argv[3].split(".")[0]
	db = MySQLdb.connect(host="192.168.4.188",
				user="hadoopuser",
				password="Hadoopuser1!",
				db=casename, charset='utf8')
	cur = db.cursor()
	cur.execute("SELECT inum FROM "+image_dir+"_ mftinfo WHERE `FN name` = 'Users' and `FN pdfme` = 5;")
	Users_inum = cur.fetchall()[0][0]
	cur.execute("select `inum`,`FN name` from "+imagedir+"_ mftinfo where `FN name` != 'Default' and `FN name` !='Public' and `FN name`!='Default User' and `FN name` != 'All Users' and `FN name`!='desktop.ini' and `FN pdfme`="+str(Users_inum));
	Userlist=[]
	for name in cur.fetchall():
		Userlist.append(name)
	db.close()
	return Userlist

def mkdir_user(argv,userlist):
	image_dir = argv[3].split(".")[0]

	for user_inum, user in userlist:
		os.mkdir("%s/%s/%s/user/%s" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/web" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/web/chrome" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/web/chrome/history" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/web/chrome/cache" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/web/ie" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/web/ie/history" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/web/ie/cache" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/web/edge" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/web/edge/history" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/web/edge/cache" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/jumplist" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/jumplist/auto" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/jumplist/custom" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/linkfile" %(argv[1], argv[2], image_dir, user))
		os.mkdir("%s/%s/%s/user/%s/iconcache" %(argv[1], argv[2], image_dir, user))

def run(argv):
	if check_argument(argv) :
		exit(1)
	userlist = user_info(argv)

	try :
		mkdir_user(argv, userlist)
	except :
		pass

	webartifact_extract.extract_artifact(argv, userlist)
	jumplist_extract.extract_artifact(argv,userlist)
	linkfile_extract.extract_artifact(argv,userlist)
	iconcache_extract.extract_artifact(argv, userlist)
	registry_extract.extract_artifact(argv,userlist)

if __name__ == "__main__":
	run(sys.argv)
