# -*- coding: utf-8 -*-
# !/usr/bin/python

from email.header import Header, decode_header
import mailbox
import os
import sys
import email
import re
import os.path
import calendar
import time
import unicodecsv as csv
import io

try:
    sys.stdout=io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr =io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
except:
    pass
csvresult=[]

def email_time_to_timestamp(s):
    tt = email.utils.parsedate_tz(s)
    if tt is None: return None
    return calendar.timegm(tt) - (tt[9]-32400)

def extract_message_payload(msg):
    """
    Extracts recursively the payload of the messages contained in :mes:
    When a message is embedded in another, it uses the parameter :parent_subject:
    to set the subject properly (it uses the parent's subject)
    """
    csvlist = {}
    csvlist['Subject'] = ''
    csvlist['To'] = ''
    csvlist['To_name'] = ''
    csvlist['From'] = ''
    csvlist['From_name'] = ''
    csvlist['Cc'] = ''
    csvlist['Bcc'] = ''
    csvlist['Date'] = ''
    csvlist['IP'] = ''
    csvlist['Body'] = ''
    csvlist['htmlBody'] = ''
    csvlist['Attachments_list'] = ''
    csvlist['Attachments_count'] = ''


    if msg.is_multipart():
        subject = msg.get("subject")

        try:
            dh_subject = decode_header(subject)
            subject = dh_subject[0][0]
            subjectcode = dh_subject[0][1]


            if subjectcode != None:
                subject = subject.decode(subjectcode, 'ignore')
                csvlist['Subject'] = subject
            else:
                csvlist['Subject'] = dh_subject[0][0]

        except:
            csvlist['Subject'] = None
            pass

        '''
        # messageid
        message_id = ""
        try:
            message_id = msg.get("Message-ID")

            logging.debug("message_id: " + message_id)
        except:
            message_id = str(uuid.uuid4())
            logging.warning("Fail To Get Message_id. Use Random UUID:%s", message_id)
        '''

        # parse and decode to
        to_username = ""
        to_domain = ""

        try:
            if (msg.get("to") != None):
                hmail_tos = msg.get("to").split(',')
                for hmail_to in hmail_tos:
                    hmail_to = email.utils.parseaddr(hmail_to)
                    ptr = hmail_to[1].find('@')
                    to_username = hmail_to[1][:ptr]
                    to_domain = hmail_to[1][ptr:]
                    csvlist['To'] += to_username + to_domain + '\n'
                    if email.header.make_header(decode_header(hmail_to[0])) == '':
                        csvlist['To_name'] += ' ' + '\n'
                    else:
                        csvlist['To_name'] += str(email.header.make_header(decode_header(hmail_to[0]))) + '\n'

        except:
            print('debug')
        csvlist['To'] = csvlist['To'][:-1]
        csvlist['To_name'] = csvlist['To_name'][:-1]

        # parse and decode from
        from_username = ""
        from_domain = ""

        csvlist['From'] = ''
        csvlist['From_name'] = ''

        try:
            hmail_from = email.utils.parseaddr(msg.get("from"))
            ptr = hmail_from[1].find('@')
            from_username = hmail_from[1][:ptr]
            from_domain = hmail_from[1][ptr:]
            csvlist['From'] = from_username + from_domain
            csvlist['From_name'] = str(email.header.make_header(decode_header(hmail_from[0])))
        except:
            csvlist['From_name'] = None

        # parse and decode Cc
        cc_username = ""
        cc_domain = ""
        try:
            if (msg.get("Cc") != None):
                hmail_ccs = msg.get("Cc").split(',')
                for hmail_cc in hmail_ccs:
                    hmail_cc = email.utils.parseaddr(hmail_cc)
                    ptr = hmail_cc[1].find('@')
                    cc_username = hmail_cc[1][:ptr]
                    cc_domain = hmail_cc[1][ptr:]
                    csvlist['Cc'] += cc_username + cc_domain + '\n'
            csvlist['Cc'] = csvlist['Cc'][:-1]
        except:
            cc_username = ""
            cc_domain = ""
            csvlist['Cc'] = None

        try:
            if (msg.get("Bcc") != None):
                hmail_ccs = msg.get("Bcc").split(',')
                for hmail_cc in hmail_ccs:
                    hmail_cc = email.utils.parseaddr(hmail_cc)
                    ptr = hmail_cc[1].find('@')
                    cc_username = hmail_cc[1][:ptr]
                    cc_domain = hmail_cc[1][ptr:]
                    csvlist['Bcc'] += cc_username + cc_domain + '\n'
            csvlist['Bcc'] = csvlist['Bcc'][:-1]
        except:
            cc_username = ""
            cc_domain = ""
            csvlist['Bcc'] = None
        # parse and decode Date

        try:
            csvlist['Date'] = time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime(email_time_to_timestamp(msg.get("Date"))))
        except:
            csvlist['Date'] = None

        # parse and decode sender ip
        IP = ""
        try:
            hmail_recv = msg.get("X-Originating-IP")
            if (hmail_recv != None):
                hmail_recv = hmail_recv.strip("[]")
                IP = hmail_recv
            else:
                hmail_receiveds = msg.get_all("Received")
                if (hmail_receiveds != None):
                    for hmail_received in hmail_receiveds:
                        m = re.findall(r'from[^\n]*\[(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])', hmail_received)
                        if (len(m) >= 1):
                            hmail_recv = re.findall(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])', m[0])
                            if (len(hmail_recv) >= 1):
                                IP = hmail_recv[0]
            csvlist['IP'] = IP

        except:
            csvlist['IP'] = None

        # header end
        # body start
        counter = 1
        for part in msg.walk():
            try:
                if (part.get('Content-Disposition') != None):
                    counter += 1
                    # this part is an attachment
                    if type(decode_header(part.get('Content-Disposition'))[0][0])==type(bytes()):
                        filename = decode_header(part.get('Content-Disposition'))[1][0] #disgusting code
                    name = part.get_filename()
                    name = str(email.header.make_header(decode_header(name)))

                    try:
                        h = email.Header.Header(name)
                        dh = email.Header.decode_header(h)
                        filename = dh[0][0]
                        filecode = dh[0][1]
                        if (filecode != None):
                            filename = filename.decode(filecode, 'ignore')
                        if not filename:
                            filename = 'part-%03d' % (counter)
                    except:
                        filename = name
                    csvlist['Attachments_count'] = str(counter - 1)

                    csvlist['Attachments_list'] += filename + '\n'

                    if (os.path.exists('./attachments') == False):
                        os.mkdir("./attachments")
                    fp = open(os.path.join('./attachments/', filename), 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
                    continue

            except:
                filename = decode_header(part.get('Content-Disposition'))[0][0].decode('utf-8')

                filename = filename[filename.find('"') + 1:-1]
                csvlist['Attachments_count'] = str(counter - 1)
                csvlist['Attachments_list'] += filename + '\n'
                if (os.path.exists('./attachments') == False):
                    os.mkdir("./attachments")
                fp = open(os.path.join('./attachments/', filename), 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
                continue


            # attachment

            if part.get_content_maintype() == 'multipart':
                continue
            # content plain
            content_plain = ""

            try:
                if (part.get_content_type() == "text/plain"):
                    code = part.get_content_charset()
                    if (code == None):
                        content_plain = part.get_payload()
                    else:
                        content_plain = part.get_payload(decode=True).decode('utf-8')
                        if content_plain[:2] == '\\u':
                            content_plain = bytes(content_plain, 'utf-8').decode('unicode-escape')
                        # print(content_plain.encode('utf-8').decode('unicode-escape'))
                        csvlist['Body'] = content_plain

                    continue
            except:
                csvlist['Body'] = None

            # content html
            content_html = ""
            try:
                if (part.get_content_type() == "text/html"):
                    code = part.get_content_charset()

                    if (code == None):
                        content_html = part.get_payload()
                        csvlist['htmlBody'] = str(content_html)
                    else:
                        try:
                            content_html = part.get_payload(decode=True).decode(code, 'ignore')
                            csvlist['htmlBody'] = content_html
                        except:
                            content_html = part.get_payload(decode=True).decode('GBK', 'ignore')
                            csvlist['htmlBody'] = str(content_html)

                        # logging.debug(content_html.encode('GBK', 'ignore'))
                    continue
            except:
                csvlist['htmlBody'] = None
        csvlist['Attachments_list'] = csvlist['Attachments_list'][:-1]
        csvresult.append(csvlist)

def extract_mbox_file(file):
    """
    Extracts all the messages included in an mbox :file:
    by calling extract_message_payload
    """
    mbox = mailbox.mbox(file)
    for message in mbox:
        extract_message_payload(message)

def csvReport(csv_list):
    if not len(csv_list):
        #print("Empty message not processed")
        return
    # CSV Report
    fout_path='email_result.csv'
    if os.path.isfile(fout_path)==True:
        with open(fout_path, 'ab')as fout:
            header = ['Subject', 'To', 'To_name', 'From', 'From_name', 'Cc', 'Bcc', 'Date', 'IP', 'Body', 'htmlBody',
                      'Attachments_list', 'Attachments_count']
            fout.write(u'\ufeff'.encode('utf8'))
            csv_fout = csv.DictWriter(fout, fieldnames=header, extrasaction='ignore', encoding='utf-8')
            csv_fout.writeheader()
            csv_fout.writerows(list(csv_list))
    else:
        with open(fout_path, 'wb')as fout:
            header = ['Subject', 'To', 'To_name', 'From', 'From_name', 'Cc', 'Bcc', 'Date', 'IP', 'Body', 'htmlBody','Attachments_list', 'Attachments_count']
            fout.write(u'\ufeff'.encode('utf8'))
            csv_fout = csv.DictWriter(fout, fieldnames=header, extrasaction='ignore', encoding='utf-8')
            csv_fout.writeheader()
            csv_fout.writerows(list(csv_list))
        fout.close()

if __name__ == '__main__':
    argv = sys.argv
    root_dir = argv[1]
    if os.path.isdir(argv[1])==True:
        for (root, dirs, files) in os.walk(root_dir):
            if len(files) > 0:
                for file_name in files:
                    extract_mbox_file(os.path.join(root,file_name))
    csvReport(csvresult)

