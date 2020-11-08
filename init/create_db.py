import MySQLdb
import sys
if __name__=="__main__":
	db = MySQLdb.connect(host="192.168.4.188",
				user="hadoopuser",
				password="Hadoopuser1!")
	cur=db.cursor()
	cur.execute("create database " + sys.argv[1])
	db.commit()
	db.close()
