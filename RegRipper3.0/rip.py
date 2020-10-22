import subprocess
import sys
import csv

#pipeusb = subprocess.Popen(["perl", "/plugins/usb.pl"], stdout=subprocess.PIPE)

f=open('output.csv', 'w', encoding='utf-8')

pipe = subprocess.Popen(["perl", "rip.pl", "-r", sys.argv[1], "-p", sys.argv[2],"-c"])

pipe.communicate()
