# -*- coding: utf-8 -*-

import sys
import argparse
import logging
import jinja2
import io
import pypff
import re
from collections import Counter
from email.header import decode_header
from email.utils import parsedate_tz
from datetime import datetime
import time
import calendar
import email.utils
import os
import logging
import io
import pypff
import unicodecsv as csv
from collections import Counter

csvlist = []

#def main(file_name,result):
def main():
    opst=pypff.file()
    opst.open('1234.pst')
    root=opst.get_root_folder()
    #csvReport(parse_folder(root),result)
    csvReport(parse_folder(root))
def prep(b):
    if type(b) == bytes:
        try:
            b = b.decode("utf8")
        except UnicodeDecodeError:
            pass
        else:
            return b.strip() if b else None
        try:
            b = b.decode("cp1252")
        except UnicodeDecodeError:
            return None
        else:
            return b.strip() if b else None
    return b.strip() if b else None

def email_time_to_timestamp(s):
    tt = email.utils.parsedate_tz(s)
    if tt is None: return None
    return calendar.timegm(tt) - (tt[9]-32400)

def parse_folder(base):                     #1.folder 2.subject 3.To 4.Sender 5.Sendername 6.date 7.Body 8.attachment_counts
    messages = []
    for folder in base.sub_folders:
        if folder.number_of_sub_folders:
            messages += parse_folder(folder)
        for message in folder.sub_messages:
            tempcsvlist={}
            tempcsvlist['Folder']=folder.name
            tempcsvlist['Subject']=message.subject
            #print(message.transport_headers,message.subject)
            #--------------------------------------------To 찾기
            try:
                buf=io.StringIO(message.transport_headers)
                for i in message.transport_headers:
                    tempstr=buf.readline()
                    if tempstr[0:3]=='To:':
                        pattern = "([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+)(\.[a-zA-Z]*)"
                        tempstr = message.transport_headers[message.transport_headers.find(tempstr):]
                        if (tempstr[3:].find(':'))==-1:
                            tempstr = re.findall(pattern, tempstr)
                        else:
                            tempstr=(tempstr[:tempstr[3:].find(':')+3])
                            tempstr=re.findall(pattern,tempstr)
                        if(len(tempstr)==0):
                            tempcsvlist['To']=None
                            break
                        str_result=''
                        for j in range(len(tempstr)):
                            str_result+=tempstr[j][0]+'@'+tempstr[j][1]+tempstr[j][2]+' '
                        tempcsvlist['To']=str_result
                        break
                    else:
                        continue
            except:
                tempcsvlist['To']=None
                pass
            #--------------------------------------------Sender 찾기
            try:
                pattern = "From:.*([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+)(\.[a-zA-Z]*)"
                temp=re.search(pattern, message.transport_headers).group()
                pattern = "([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+)(\.[a-zA-Z]*)"
                tempcsvlist['Sender']=re.search(pattern,temp).group()
            except:
                try:
                    for i in range (len(message.transport_headers)):
                        tempstr=message.transport_headers[message.transport_headers.find('From:'):]
                        if tempstr[0].islower():
                            i=message.transport_headers.find('From:')+1
                        elif tempstr.find("<>") != -1:
                            tempcsvlist['Sender']=None
                            break
                        else:
                            pattern = "([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+)(\.[a-zA-Z]*)"
                            tempcsvlist['Sender']=re.search(pattern,tempstr).group()
                            break
                except:
                    tempcsvlist['Sender']=None
                    pass
                pass
            #-----------------------------------------------sender_name 추가
            tempcsvlist['Sender_name']=message.sender_name
            #-----------------------------------------------
            #-----------------------------------------------date 추가
            pattern = "Date:\s.*[0-9]*[\s][A-Za-z]*[\s]\d*[\s]\d*:\d*:\d*.[^(\s]*"
            try:
                tempdate = re.search(pattern, message.transport_headers).group()
                pattern = "[0-9]*[\s][A-Za-z]*[\s]\d*[\s]\d*:\d*:\d*.[^(\s]*"
                tempdate = re.search(pattern, tempdate).group()
                tempcsvlist['Date']=time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime(email_time_to_timestamp(tempdate)))
            except:
                try:
                    pattern = "[0-9]*[\s][A-Za-z]*[\s]\d*[\s]\d*:\d*:\d*.[^(\s]*"
                    tempdate = re.search(pattern, message.transport_headers).group()
                    tempcsvlist['Date']=time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime(email_time_to_timestamp(tempdate)))
                except:
                    tempcsvlist['Date']=None

            #-----------------------------------------------메시지 본문 추가
            tempcsvlist['Body']=prep(message.plain_text_body)
            #-----------------------------------------------첨부파일 개수 추가
            tempcsvlist['Attachments_count']=str(message.number_of_attachments)
            #-----------------------------------------------
            csvlist.append(tempcsvlist)

    return csvlist

#def csvReport(message_list,result):
def csvReport(message_list):
    if not len(message_list):
        #print("Empty message not processed")
        return

    # CSV Report
    #fout_path = result+ ".csv"
    fout_path='test1235.csv'
    with open(fout_path, 'wb')as fout:
        header = ['Folder', 'Subject', 'To', 'Sender', 'Sender_name', 'Date', 'Body','Attachments_count']
        fout.write(u'\ufeff'.encode('utf8'))
        csv_fout = csv.DictWriter(fout, fieldnames=header, extrasaction='ignore', encoding='utf-8')

        csv_fout.writeheader()
        csv_fout.writerows(message_list)
        
    fout.close()

main()
#main(sys.argv[1],sys.argv[2])