import requests, time
from datetime import datetime
from dateutil import tz
import paramiko
from scp import SCPClient
import pymysql
from tabulate import tabulate
import re
import sys

def UTC_to_KST(s):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Seoul')
    # METHOD 2: Auto-detect zones:
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    # utc = datetime.utcnow()
    utc = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

    # Tell the datetime object that it's in UTC time zone since
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    central = utc.astimezone(to_zone)
    return central

def Visualize_MFT(casename):
    db = pymysql.connect(host='192.168.4.188', user='hadoopuser', password='Hadoopuser1!', db=casename, charset='utf8')
    cur = db.cursor()
    sql = 'select Image_Name from Disk_Image'
    cur.execute(sql)
    Image_list = list(cur.fetchall())
    column=[]
    for i in range(0,len(Image_list)):
        sql = """select Document_ID, File_Path, Sha256, Create_Time,Modify_Time,Access_Time from Document natural join MFT_Entry where Document.Artifact_ID in (select Artifact_ID from Artifact natural join Disk_Image where Image_Name='%s') order by Document_ID desc;""" % \
              Image_list[i][0]
        cur.execute(sql)
        column.append(list(cur.fetchall()))

    temp=''

    for i in range(len(column)-1,-1,-1):
        for j in range(0,len(column[i])):
            temp+="%s;%s;%s;%s;%s;%s;%s;%s\n"%(column[i][j][0],column[i][j][1].split('\\')[-1],column[i][j][1],column[i][j][2],column[i][j][3],column[i][j][4],column[i][j][5],Image_list[i][0])

    f=open("/hdfs/%s/VisualizeMFT_result.txt"%casename,'w')
    f.write(temp)
    f.close()

def Visualize_Email(casename):
    db = pymysql.connect(host='192.168.4.188', user='hadoopuser', password='Hadoopuser1!', db=casename,
                         charset='utf8')
    cur = db.cursor()

    sql="""select Attach_ID,Mail_To,Mail_From,Attach_File_Name,Sha256,Subject,Date,Image_Name,Artifact_Name from Email natural join Artifact natural join  Disk_Image natural join Email_Attach natural join Email_Receiver order by Attach_ID DESC;"""
    cur.execute(sql)
    column = list(cur.fetchall())

    temp=''
    for i in range(0,len(column)):
        temp+="%s;^;%s;^;%s;^;%s;^;%s;^;%s;^;%s;^;%s;^;%s(!@#)" %(column[i][0],column[i][1],column[i][2],column[i][3],column[i][4],column[i][5],column[i][6],column[i][7],column[i][8])

    f=open("/hdfs/%s/VisualizeEmail_result.txt"%casename,'w')
    f.write(temp)
    f.close()

def Visualize_URL(casename):
    db = pymysql.connect(host='192.168.4.188', user='hadoopuser', password='Hadoopuser1!', db=casename,
                         charset='utf8')
    cur = db.cursor()
    # body에 url 있는 메일 리스트 출력
    sql = """select Email.Email_ID, Email_Receiver.Mail_To, Email.Mail_From, Email.Subject,Email.Body, Email.Date from Email,Email_Receiver where Email.Email_ID=Email_Receiver.Email_ID and Body regexp 'http[s]?:[a-zA-Z0-9/.!?+*(),$\-@\.&+:/?=]*' order by Email_ID DESC;"""
    cur.execute(sql)
    column = list(cur.fetchall())

    temp=''
    for i in range(0,len(column)):
        temp+="%s;^;%s;^;%s;^;%s;^;%s;^;%s(!@#)" %(column[i][0],column[i][1],column[i][2],column[i][3],column[i][4],column[i][5])

    f=open("/hdfs/%s/VisualizeURL_result.txt"%casename,'w')
    f.write(temp)
    f.close()

def Extract_File(user_input,user_select,casename):
    db = pymysql.connect(host='192.168.4.188', user='hadoopuser', password='Hadoopuser1!', db=casename,
                         charset='utf8')
    cur = db.cursor()
    if user_select=='3':
        sql = """select MFT_Entry_Number, File_Local_Path from Document where Document_ID='%s';"""%user_input
        cur.execute(sql)
        column = cur.fetchone()
        try:
            route = column[1].replace(column[1].split('/')[-1], str(column[0]) + '#' + column[1].split('/')[-1])+';'+column[1].split('/')[-1]
        except:
            route="Error"
        f = open("/hdfs/%s/ExtractFile_MFTresult.txt"%casename, 'w')
        f.write(route)
        f.close()
    else:
        sql = """select Attach_File_Path from Email_Attach where Attach_ID='%s';""" % user_input
        cur.execute(sql)
        column = cur.fetchone()

        try:
            route = column[0]
        except:
            route="Error"
        f = open("/hdfs/%s/ExtractFile_Emailresult.txt"%casename, 'w')
        f.write(route)
        f.close()

def Verify_File(user_input, user_select,casename):
    db = pymysql.connect(host='192.168.4.188', user='hadoopuser', password='Hadoopuser1!', db=casename,
                         charset='utf8')
    cur = db.cursor()

    if user_select == '5':
        sql = """select MFT_Entry_Number, File_Local_Path from Document where Document_ID='%s';"""%user_input
        cur.execute(sql)
        column = cur.fetchone()
        try:
            if column[1]=='OneDrive':
                f = open("/hdfs/%s/MFT_File%s_Verifyresult.txt" % (casename, user_input), 'w')
                f.write('OneDrive')
                f.close()
                return

            filename=column[1].split('/')[-1]
            file = column[1].replace(column[1].split('/')[-1], str(column[0]) + '#' + column[1].split('/')[-1])
        except:
            f = open("/hdfs/%s/MFT_File%s_Verifyresult.txt" % (casename,user_input), 'w')
            f.write('Error')
            f.close()
            return
    else:

        sql = """select Attach_File_Path from Email_Attach where Attach_ID='%s';""" % user_input
        cur.execute(sql)
        column = cur.fetchone()

        try:
            filename=column[0].split('/')[-1]
            file = column[0]
        except:
            f = open("/hdfs/%s/Email_File%s_Verifyresult.txt" % (casename,user_input), 'w')
            f.write('Error')
            f.close()
            return

    # 바이러스토탈 API Key
    my_apikey = '463a28054406934b9a6fff29e5ff304a683574f69f171cd9a91d813eab8d01ae'
    print(file)
    # 바이러스 의심 파일 설정
    files = {'file': (file, open(file, 'rb'))}

    # 바이러스토탈 파일 스캔 주소
    url_scan = 'https://www.virustotal.com/vtapi/v2/file/scan'
    url_scan_params = {'apikey': my_apikey}
    # 바이러스토탈 파일 스캔 시작
    response_scan = requests.post(url_scan, params=url_scan_params, files=files)
    result_scan = response_scan.json()
    scan_resource = result_scan['resource']


    #print('Virustotal FILE SCAN START (25 Seconds Later) : ', file, '\n')

    # 스캔 후 80초 대기
    time.sleep(80)

    # 바이러스토탈 파일 스캔 결과 주소
    url_report = 'https://www.virustotal.com/vtapi/v2/file/report'
    url_report_params = {'apikey': my_apikey, 'resource': scan_resource}

    # 바이러스토탈 파일 스캔 결과 리포트 조회
    response_report = requests.get(url_report, params=url_report_params)

    report_message=''
    try:
        # 점검 결과 데이터 추출
        report = response_report.json()
        report_scan_date = report.get('scan_date')
        report_scan_sha256 = report.get('sha256')
        report_scan_md5 = report.get('md5')
        report_scan_result = report.get('scans')
        report_scan_vendors = list(report['scans'].keys())
        report_scan_vendors_cnt = len(report_scan_vendors)
    except:
        if user_select == '5':
            f = open("/hdfs/%s/MFT_File%s_Verifyresult.txt" % (casename,user_input), 'w')
        else:
            f = open("/hdfs/%s/Email_File%s_Verifyresult.txt" % (casename,user_input), 'w')
        f.write('Error')
        f.close()
        return

    # 파일 스캔 결과 리포트 데이터 보기
    report_message+='Scan Date (KST) : %s\n' % UTC_to_KST(report_scan_date).strftime("%Y-%m-%d %H:%M:%S")
    report_message+='Scan File SHA256 : %s\n' % report_scan_sha256
    report_message+='Scan File MD5 : %s\n'% report_scan_md5
    report_message+='Scan File Vendor CNT : %s;'% report_scan_vendors_cnt

    threat_count = 0
    # 바이러스 스캔 엔진사별 데이터 정리
    for vendor in report_scan_vendors:
        outputs = report_scan_result[vendor]
        outputs_result = report_scan_result[vendor].get('result')
        outputs_version = report_scan_result[vendor].get('version')
        outputs_detected = report_scan_result[vendor].get('detected')
        outputs_update = report_scan_result[vendor].get('update')

        report_message+='%s^%s^%s^%s\n' % (vendor,outputs_version,outputs_detected,outputs_result)

        if not outputs_result == None:
            threat_count += 1

    report_message='It was detected as malicious code in %d vaccines.\n\n' % threat_count + report_message

    if threat_count > 30:
        report_message="%s is almost malicious file.\n"%filename + report_message
    elif threat_count > 15:
        report_message="%s is probably malicious file.\n"%filename + report_message
    elif threat_count == 0:
        report_message="%s is safe File.\n"%filename +report_message
    else:
        report_message="%s is more verification require file.\n"%filename + report_message

    # 점검 완료 메시지
    report_message = report.get('verbose_msg') + '\n\n' +report_message

    if user_select == '5':
        f = open("/hdfs/%s/MFT_File%s_Verifyresult.txt"%(casename,user_input), 'w')
    else:
        f = open("/hdfs/%s/Email_File%s_Verifyresult.txt"%(casename,user_input), 'w')
    f.write(report_message)
    f.close()

def Search_File(user_input, user_select,casename):
    db = pymysql.connect(host='192.168.4.188', user='hadoopuser', password='Hadoopuser1!', db=casename,
                         charset='utf8')
    cur = db.cursor()

    if user_select == '7':
        sql = """select SHA256,File_Local_Path from Document where Document_ID='%s';""" % user_input
        cur.execute(sql)
        result = cur.fetchone()
        Hash = result[0]
        Filename = result[1].split('/')[-1]
    else:
        sql = """select SHA256,Attach_File_Name from Email_Attach where Attach_ID='%s';""" % user_input
        cur.execute(sql)
        result = cur.fetchone()
        Hash = result[0]
        Filename = result[1].split('/')[-1]

    print(Hash)

    # 바이러스토탈 API Key
    my_apikey = '463a28054406934b9a6fff29e5ff304a683574f69f171cd9a91d813eab8d01ae'

    # 바이러스 의심 파일 설정

    url_scan = 'https://www.virustotal.com/vtapi/v2/file/report'

    url_scan_params = {'resource': Hash, 'apikey': my_apikey}
    response_scan = requests.post(url_scan, params=url_scan_params)
    result_scan = response_scan.json()
    scan_resource = result_scan['resource']

    # Hash 스캔 시작 안내

    # Hash 스캔 후 6초 대기
    time.sleep(6)

    # 바이러스토탈 파일 스캔 결과 주소
    url_report = 'https://www.virustotal.com/vtapi/v2/file/report'
    url_report_params = {'apikey': my_apikey, 'resource': scan_resource}

    # 바이러스토탈 파일 스캔 결과 리포트 조회
    response_report = requests.get(url_report, params=url_report_params)
    report_message = ''
    try:
        # 점검 결과 데이터 추출
        report = response_report.json()
        report_scan_date = report.get('scan_date')
        report_scan_sha256 = report.get('sha256')
        report_scan_md5 = report.get('md5')
        report_scan_result = report.get('scans')
        report_scan_vendors = list(report['scans'].keys())
        report_scan_vendors_cnt = len(report_scan_vendors)
    except:
        if user_select == '7':
            f = open("/hdfs/%s/MFT_File%s_Searchresult.txt" % (casename,user_input), 'w')
        else:
            f = open("/hdfs/%s/Email_File%s_Searchresult.txt" % (casename,user_input), 'w')
        f.write('%s has No Result.\n\nYou can try verify.'%Filename)
        f.close()
        return

    # 파일 스캔 결과 리포트 데이터 보기
    report_message += 'Scan Date (KST) : %s\n' % UTC_to_KST(report_scan_date).strftime("%Y-%m-%d %H:%M:%S")
    report_message += 'Scan File SHA256 : %s\n' % report_scan_sha256
    report_message += 'Scan File MD5 : %s\n' % report_scan_md5
    report_message += 'Scan File Vendor CNT : %s;' % report_scan_vendors_cnt

    threat_count = 0

    # 바이러스 스캔 엔진사별 데이터 정리
    for vendor in report_scan_vendors:
        outputs = report_scan_result[vendor]
        outputs_result = report_scan_result[vendor].get('result')
        outputs_version = report_scan_result[vendor].get('version')
        outputs_detected = report_scan_result[vendor].get('detected')
        outputs_update = report_scan_result[vendor].get('update')

        report_message += '%s^%s^%s^%s\n' % (vendor, outputs_version, outputs_detected, outputs_result)

        if not outputs_result == None:
            threat_count += 1

    report_message = 'It was detected as malicious code in %d vaccines.\n\n' % threat_count + report_message
    if threat_count > 30:
        report_message = "%s is almost malicious file.\n" % Filename + report_message
    elif threat_count > 15:
        report_message = "%s is probably malicious file.\n" % Filename + report_message
    elif threat_count == 0:
        report_message = "%s is safe File.\n" % Filename + report_message
    else:
        report_message = "%s is more verification require file.\n" % Filename + report_message

    # 점검 완료 메시지
    report_message = report.get('verbose_msg') + '\n\n' + report_message
    if user_select == '7':
        f = open("/hdfs/%s/MFT_File%s_Searchresult.txt" % (casename,user_input), 'w')
    else:
        f = open("/hdfs/%s/Email_File%s_Searchresult.txt" % (casename,user_input), 'w')
    f.write(report_message)
    f.close()

def Verify_URL(URL,filename,casename):
    # 바이러스토탈 API Key
    my_apikey = '463a28054406934b9a6fff29e5ff304a683574f69f171cd9a91d813eab8d01ae'

    # 바이러스토탈 파일 스캔 주소
    url_scan = 'https://www.virustotal.com/vtapi/v2/url/scan'
    url_scan_params = {'apikey': my_apikey, 'url': URL}
    # 바이러스토탈 파일 스캔 시작
    response_scan = requests.post(url_scan, params=url_scan_params)
    result_scan = response_scan.json()
    scan_resource = result_scan['url']


    # URL 스캔 후 6초 대기
    time.sleep(6)

    # 바이러스토탈 파일 스캔 결과 주소
    url_report = 'https://www.virustotal.com/vtapi/v2/url/report'
    url_report_params = {'apikey': my_apikey, 'resource': scan_resource}

    # 바이러스토탈 파일 스캔 결과 리포트 조회
    response_report = requests.get(url_report, params=url_report_params)

    report_message=''
    try:
        # 점검 결과 데이터 추출
        report = response_report.json()
        report_scan_result = report.get('scans')
        report_scan_vendors = list(report['scans'].keys())
        report_scan_vendors_cnt = len(report_scan_vendors)
        report_scan_date = report.get('scan_date')
        report_scan_result = report.get('scans')
        report_scan_vendors = list(report['scans'].keys())
        report_scan_vendors_cnt = len(report_scan_vendors)
    except:
        f = open("/hdfs/%s/URL%s_Verifyresult.txt" % (casename,filename), 'w')
        f.write('%s has No Result.\n\nYou can try verify.' % URL)
        f.close()
        return

    report_message += 'Scan Date (KST) : %s\n' % UTC_to_KST(report_scan_date).strftime("%Y-%m-%d %H:%M:%S")
    report_message += 'Scan File Vendor CNT : %s;' % report_scan_vendors_cnt


    for vendor in report_scan_vendors:
        outputs = report_scan_result[vendor]
        outputs_result = report_scan_result[vendor].get('result')
        outputs_version = report_scan_result[vendor].get('version')
        outputs_detected = report_scan_result[vendor].get('detected')
        outputs_update = report_scan_result[vendor].get('update')

        report_message+='%s^%s^%s^%s\n' % (vendor,outputs_version,outputs_detected,outputs_result)
        threat_count = 0

        if not outputs_result == None:
            threat_count += 1
    report_message = 'It was detected as malicious code in %d vaccines.\n\n' % threat_count + report_message
    if threat_count > 10:
        report_message="%s is Almost malicious URL"%URL + report_message
    elif threat_count > 5:
        report_message="%s is Probably malicious URL"%URL + report_message
    elif threat_count == 0:
        report_message="%s is Safe URL"%URL
    else:
        report_message="%s is More Verification require URL.\n" %URL + report_message


    # 점검 완료 메시지
    report_message = report.get('verbose_msg') + '\n\n' + report_message
    f = open("/hdfs/%s/URL%s_Verifyresult.txt" % (casename,filename),'w')
    f.write(report_message)
    f.close()

if __name__ == '__main__':
    user_input=sys.argv

    if user_input[1]=='0':
        Visualize_MFT(user_input[2]) # case 적용
    elif user_input[1]=='1':
        Visualize_Email(user_input[2]) # case 적용
    elif user_input[1]=='2':
        Visualize_URL(user_input[2]) # case 적용
    elif user_input[1]=='3' or user_input[1]=='4':
        Extract_File(user_input[2],user_input[1],user_input[3]) #case 적용
    elif user_input[1]=='5' or user_input[1]=='6':
        Verify_File(user_input[2],user_input[1],user_input[3]) #case 적용
    elif user_input[1]=='7' or user_input[1]=='8':
        Search_File(user_input[2],user_input[1],user_input[3]) #case 적용
    elif user_input[1]=='9':
        Verify_URL(user_input[2],user_input[3],user_input[4]) #case 적용
