import pymysql
import networkx as nx
import os, sys,math
from tabulate import tabulate
import matplotlib.font_manager
from matplotlib import font_manager, rc
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import numpy as np

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

def Visualize(casename):
    graph = nx.Graph()

    db= pymysql.connect(host='192.168.4.188', user='hadoopuser', password='Hadoopuser1!', db=casename, charset='utf8')
    cur = db.cursor()
    sql = 'select Mail_To,Mail_From,Date,Subject from Email_Receiver natural join Email order by Date;'
    cur.execute(sql)
    temp_edge = cur.fetchall()
    temp_edge = list(set(list(temp_edge)))
    report_address1 = ''
    report_address2 = ''
    report_size = ''
    report_whitelist = ''


    for i in range(0,len(temp_edge)):
        size=0
        tmp_1 = temp_edge[i][0]
        tmp_2 = temp_edge[i][1]
        for j in range(0, len(temp_edge)):
            if temp_edge[j][1]==tmp_2 and temp_edge[j][0]==tmp_1:
                size+=1
            if temp_edge[j][1]==tmp_1 and temp_edge[j][0]==tmp_2:
                size+=1
        graph.add_edge(temp_edge[i][0], temp_edge[i][1], weight=size)

        report_address1+=temp_edge[i][0]+';'
        report_address2+=temp_edge[i][1]+';'
        report_size+=str(size)+';'

    plt.figure('email_Visualize', figsize=(len(temp_edge), len(temp_edge)))

    pos = nx.spring_layout(graph)
    nx.draw(graph, pos=pos, with_labels=True)
    labels=nx.get_edge_attributes(graph,'weight')
    nx.draw_networkx_edge_labels(graph, pos,edge_labels=labels)

    try:
        sql = '''select Email_Address from Email_WhiteList;'''
        cur.execute(sql)
        templist = cur.fetchall()

        templist = list(set(list(templist)))
        whitelist=[]
        for i in range(0,len(templist)):
            report_whitelist+=templist[i][0]+';'
            whitelist.append(templist[i][0])
        nx.draw_networkx_nodes(graph,pos,nodelist=whitelist,node_color='#00CE2C',node_size=1000)
    except:
        pass
    plt.margins(x=1, y=1)
    try:
        plt.savefig("/hdfs/%s/report/E-mail_Visualize.png"%casename,bbox_inches='tight')
    except:
        pass
    f = open("/home/hadoopuser/Email_Visualize.txt", 'w')
    f.write('Visualize\n%s\n%s\n%s\n%s'%(report_address1,report_address2,report_size,report_whitelist))
    f.close()

def View_Email(casename):
    db = pymysql.connect(host='192.168.4.188', user='hadoopuser', password='Hadoopuser1!', db=casename,
                         charset='utf8')
    cur = db.cursor()

    sql = """select Email.Email_ID,Mail_To,Mail_From,Subject,Attach_File_Name,Body,Date,Image_Name,Artifact_Name from Email left join Email_Attach on Email.Email_ID=Email_Attach.Email_ID natural join Artifact natural join Disk_Image inner join Email_Receiver on Email.Email_ID=Email_Receiver.Email_ID order by Email_ID desc;"""
    cur.execute(sql)
    column = list(cur.fetchall())

    temp = ''
    for i in range(0, len(column)):
        temp += "%s;^;%s;^;%s;^;%s;^;%s;^;%s;^;%s;^;%s;^;%s(!@#)" % (
            column[i][0], column[i][1], column[i][2], column[i][3], column[i][4], column[i][5], column[i][6],
            column[i][7], column[i][8])

    f = open("/hdfs/%s/View_Email_result.txt" %casename, 'w')
    f.write(temp)
    f.close()

def View_Frequency(input_date,casename):
    db = pymysql.connect(host='192.168.4.188', user='hadoopuser', password='Hadoopuser1!', db=casename,
                         charset='utf8')
    cur = db.cursor()

    sql = '''select Email_Address from Email_WhiteList;'''
    cur.execute(sql)
    templist = cur.fetchall()


    templist = list(set(list(templist)))
    employee = []
    for i in range(0, len(templist)):
        employee.append(templist[i][0])



    date_count = []
    mail_address = []
    for i in range(0,len(employee)):
        temp_count = [0 for i in range(24)]
        sql="""select hour(Email.Date) from Email,Email_Receiver where Email.Email_ID=Email_Receiver.Email_ID and Email.Mail_From='%s'"""%employee[i] +""" and date_format(Date,'%Y-%m-%d')="""+ """'%s';"""%input_date
        cur.execute(sql)
        sql_count=list(cur.fetchall())
        for j in range(0,len(sql_count)):
            temp_count[sql_count[j][0]]+=1
        date_count.append(temp_count)
        mail_address.append(employee[i])


    df = pd.DataFrame(data=np.array(date_count),index=mail_address,columns=list(range(0,24)))

    plt.figure(figsize=(14, 5))
    ax=sns.heatmap(df, cmap='Blues',linewidths=0.3, annot=False, fmt='d')
    plt.title('%s Mail Send Count'%input_date, fontsize=14)
    plt.xlabel('Time of Date', fontsize=14)
    plt.ylabel('Mail Address', fontsize=14)
    plt.savefig("/hdfs/%s/report/%s Mail Send Count" % (casename,input_date) + ".png", bbox_inches='tight')

def View_Frequency2(input_date,input_address,casename):

    db = pymysql.connect(host='192.168.4.188', user='hadoopuser', password='Hadoopuser1!', db=casename,
                         charset='utf8')
    cur = db.cursor()

    mail_count = []
    mail_list = []

    sql = """select Email_Receiver.Mail_To from Email, Email_Receiver where Email.Email_ID=Email_Receiver.Email_ID and Email.Mail_From='%s'""" % input_address + """ and date_format(Date,"%Y-%m-%d")="""
    sql += "'" + input_date + "'"
    cur.execute(sql)
    maillist = cur.fetchall()
    maillist = list(set(list(maillist)))

    for i in range(0, len(maillist)):
        sql = """select count(Email_Receiver.Mail_To) from Email, Email_Receiver where Email.Email_ID=Email_Receiver.Email_ID and Email.Mail_From='%s' and Email_Receiver.Mail_To='%s'""" % (
        maillist[i][0], input_address) + """and date_format(Date,"%Y-%m-%d")="""
        sql += "'" + input_date + "'"
        cur.execute(sql)
        size = cur.fetchone()[0]
        sql = """select count(Email_Receiver.Mail_To) from Email, Email_Receiver where Email.Email_ID=Email_Receiver.Email_ID and Email.Mail_From='%s' and Email_Receiver.Mail_To='%s'""" % (
            input_address, maillist[i][0]) + """and date_format(Date,"%Y-%m-%d")="""
        sql += "'" + input_date + "'"
        cur.execute(sql)
        size += cur.fetchone()[0]
        mail_count.append(size)
        mail_list.append(maillist[i][0])
    plt.figure(figsize=(14, 5))
    plt.grid(True, axis='y')
    plt.bar(mail_list, mail_count, color="skyblue")
    plt.xticks(range(len(maillist)), mail_list)
    # plt.ylim(0, max(mail_count) + math.ceil(max(mail_count) * 0.1))
    plt.xlabel('Send Mail Address list', fontsize=14)
    plt.ylabel('Comunication Count', fontsize=14)
    plt.title("%s %s_Visualize" % (input_date, input_address), fontsize=14)
    plt.legend(['%s' % input_address])
    # plt.show()
    plt.savefig("/hdfs/%s/report/%s %s_Visualize.png" % (casename,input_date, input_address), bbox_inches='tight')

def View_Attachments(filename,casename):
    if platform.system() == 'Windows':
        # 윈도우인 경우
        font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
        rc('font', family=font_name)
    elif platform.system()=='Linux':
        font_name = font_manager.FontProperties(fname="/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf").get_name()
        rc('font', family=font_name)
    else:
        # Mac 인 경우
        rc('font', family='AppleGothic')

    sqlfilename=filename.split('.')[0]
    db = pymysql.connect(host='192.168.4.188', user='hadoopuser', password='Hadoopuser1!', db=casename, charset='utf8')
    cur = db.cursor()
    graph = nx.Graph()

    try:
        sql = '''select Email_Address from Email_WhiteList;'''
        cur.execute(sql)
        templist = cur.fetchall()
        templist = list(set(list(templist)))
        whitelist=[]
        for i in range(0,len(templist)):
            whitelist.append(templist[i][0])
    except:
        pass


    sql='''select Email.Mail_From, Email_Receiver.Mail_To, Email.Subject, Email.Date, Email_Attach.Attach_File_Name from Email left join Email_Receiver on Email.Email_ID=Email_Receiver.Email_ID left join Email_Attach on Email_Receiver.Email_ID=Email_Attach.Email_ID where Attach_File_Name like "%s"'''%(sqlfilename+'%') +"""order by Date;"""
    cur.execute(sql)
    column = list(cur.fetchall())
    count = 2
    blacklist=[]
    temp_column = []
    for i in range(0, len(column)):
        if not column[i] == temp_column:
            temp_column = column[i]
            graph.add_edge(str(count - 1) + '. ' + column[i][0], str(count) + '. ' + column[i][1],filename=column[i][4])

            for j in (0,len(whitelist)-1):
                if not column[i][0] in whitelist:
                    blacklist.append(str(count - 1) + '. ' + column[i][0])
                if not column[i][1] in whitelist:
                    blacklist.append(str(count) + '. ' + column[i][1])

            count += 1
        else:
            continue

    plt.figure('%s Filename Search result Visualize' % filename,figsize=(14, 5))
    pos = nx.spring_layout(graph,k=0.8,iterations=10)


    #labels = nx.get_edge_attributes(graph)
    #nx.draw_networkx_edge_labels(graph, pos,font_family=font_name,font_size=10)
    nx.draw(graph, pos, with_labels=True)
    labels = nx.get_edge_attributes(graph, 'filename')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels,font_family=font_name,font_size=10)
    nx.draw_networkx_nodes(graph, pos, nodelist=blacklist, node_color='#FF0000', node_size=800)
    plt.margins(x=0.4, y=0.4)
    plt.savefig('/hdfs/%s/report/%s Filename Search result Visualize.png' % (casename,filename), bbox_inches='tight')

def View_Keyword(keyword,casename):
    db = pymysql.connect(host='192.168.4.188', user='hadoopuser', password='Hadoopuser1!', db=casename,charset='utf8')

    graph = nx.Graph()
    sql = """select Email.Mail_From,Email_Receiver.Mail_To,Email.Subject,Email_Attach.Attach_File_Name, Email.Date from Email left join Email_Receiver on Email.Email_ID=Email_Receiver.Email_ID left join Email_Attach on Email_Receiver.Email_ID=Email_Attach.Email_ID where match(Subject,Body) against('%s') order by Date;""" % keyword
    cur = db.cursor()
    cur.execute(sql)
    column = list(cur.fetchall())
    count = 2
    blacklist = []
    temp_column = []

    try:
        sql = '''select Email_Address from Email_WhiteList;'''
        cur.execute(sql)
        templist = cur.fetchall()
        templist = list(set(list(templist)))
        whitelist=[]
        for i in range(0,len(templist)):
            whitelist.append(templist[i][0])
    except:
        pass

    for i in range(0, len(column)):
        if not column[i] == temp_column:
            temp_column = column[i]
            graph.add_edge(str(count - 1) + '. ' + column[i][0], str(count) + '. ' + column[i][1])

            for j in (0,len(whitelist)-1):
                if not column[i][0] in whitelist:
                    blacklist.append(str(count - 1) + '. ' + column[i][0])
                if not column[i][1] in whitelist:
                    blacklist.append(str(count) + '. ' + column[i][1])

            count += 1
        else:
            continue
    plt.figure('%s Keyword Search result Visualize' % keyword, figsize=(14,6))
    pos = nx.spring_layout(graph,k=0.8,iterations=5)
    nx.draw(graph, pos, with_labels=True)
    try:
        nx.draw_networkx_nodes(graph, pos, nodelist=blacklist, node_color='#FF0000', node_size=800)
    except:
        pass
    plt.margins(x=0.4, y=0.4)
    plt.savefig('/hdfs/%s/report/%s Keyword Search result Visualize.png' % (casename,keyword), bbox_inches='tight')





if __name__ == '__main__':
    input_value=sys.argv
    select_value=len(input_value)

    if input_value[1]=='1':
        Visualize(input_value[2])
    if input_value[1]=='2':
        View_Email(input_value[2]) # case 적용
    if input_value[1]=='3':
        View_Frequency(input_value[2],input_value[3]) # case 적용
    if input_value[1]=='4':
        View_Frequency2(input_value[2],input_value[3],input_value[4]) #case 적용
    if input_value[1]=='5':
        View_Attachments(input_value[2],input_value[3]) #case 적용
    if input_value[1]=='6':
        View_Keyword(input_value[2],input_value[3]) #case 적용