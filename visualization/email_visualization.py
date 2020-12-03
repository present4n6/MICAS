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


def Visualize():
    graph = nx.Graph()

    db= pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()
    sql = 'select count(ID) from email'
    cur.execute(sql)
    count=cur.fetchone()[0]

    for i in range(1,count+1):
        temp_edge=[]
        sql = 'select Mail_From from email where ID=%d'%i
        cur.execute(sql)
        temp_edge.append(cur.fetchone()[0])
        sql = 'select Mail_To from email,email_To where email.ID=email_To.ID and email.ID=%d'%i
        cur.execute(sql)
        temp_edge.append(cur.fetchall())

        if len(temp_edge[1])>1:
            for j in range(0,len(temp_edge[1])):
                sql = '''select count(Mail_To) from email,email_To where email.ID=email_To.ID and Mail_From='%s' and Mail_To="%s"'''%(temp_edge[0],temp_edge[1][j][0])
                cur.execute(sql)
                size=cur.fetchone()[0]
                sql = '''select count(Mail_To) from email,email_To where email.ID=email_To.ID and Mail_From='%s' and Mail_To="%s"''' % (temp_edge[1][j][0], temp_edge[0])
                cur.execute(sql)
                size += cur.fetchone()[0]
                if not temp_edge[0]==temp_edge[1][j][0]:
                    graph.add_edge(temp_edge[0],temp_edge[1][j][0],weight=size)
        else:
            sql = '''select count(Mail_To) from email,email_To where email.ID=email_To.ID and Mail_From='%s' and Mail_To="%s"''' % (temp_edge[0], temp_edge[1][0][0])
            cur.execute(sql)
            size = cur.fetchone()[0]
            sql = '''select count(Mail_To) from email,email_To where email.ID=email_To.ID and Mail_From='%s' and Mail_To="%s"''' % (temp_edge[1][0][0], temp_edge[0])
            cur.execute(sql)
            size += cur.fetchone()[0]
            if not temp_edge[0] == temp_edge[1][0][0]:
                graph.add_edge(temp_edge[0],temp_edge[1][0][0],weight=size)

    plt.figure('email_Visualize', figsize=(count, count))

    pos = nx.spring_layout(graph)
    nx.draw(graph, pos=pos, with_labels=True)
    labels=nx.get_edge_attributes(graph,'weight')
    nx.draw_networkx_edge_labels(graph, pos,edge_labels=labels)

    whitelist=['phj971002@gmail.com','phj971002@cu.ac.kr']
    nx.draw_networkx_nodes(graph,pos,nodelist=whitelist,node_color='#FF1744',node_size=1000)
    plt.margins(x=1, y=1)
    plt.savefig("E-mail_Visualize" + ".png",bbox_inches='tight')


    #select = list(cur.fetchall())
    #db.commit()
    #print(select)

def Visualize_input(address):
    graph = nx.Graph()

    db = pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()
    sql = """select email_To.Mail_To from email, email_To where email.ID=email_To.ID and email.Mail_From='%s'""" % address
    cur.execute(sql)
    maillist = cur.fetchall()
    maillist = list(set(list(maillist)))

    for i in range(0,len(maillist)):
        if not address==maillist[i][0]:
            sql = """select count(email_To.Mail_To) from email, email_To where email.ID=email_To.ID and email.Mail_From='%s' and email_To.Mail_To='%s'""" % (address,maillist[i][0])
            cur.execute(sql)
            size=cur.fetchone()[0]
            sql = """select count(email_To.Mail_To) from email, email_To where email.ID=email_To.ID and email.Mail_From='%s' and email_To.Mail_To='%s'""" % (maillist[i][0],address)
            cur.execute(sql)
            size += cur.fetchone()[0]
        graph.add_edge(address, maillist[i][0], weight=size)

    plt.figure('%s Visualize'%address, figsize=(10, 10))
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos=pos, with_labels=True)
    labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)

    whitelist = []
    whitelist.append(address)
    nx.draw_networkx_nodes(graph, pos, nodelist=whitelist, node_color='#FF1744', node_size=500)
    plt.margins(x=0.4, y=0.4)
    plt.savefig('%s Visualize.png'%address, bbox_inches='tight')

def Attach_list():
    db = pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()
    sql = 'select email.ID,email_To.Mail_To,email.Mail_From,email.Subject,email_attach.Attach_File_Name, email.Date from email inner join email_To on email.ID=email_To.ID inner join email_attach on email_To.Id=email_attach.ID;'
    cur.execute(sql)

    column = list(cur.fetchall())
    column.insert(0, ['ID', 'Mail_To', 'Mail_From', 'Subject', 'Attach_File_Name','Date'])
    print(tabulate(column))

def Attach_find(filename):
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
    db = pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()
    sql = '''select email.Id, email.Subject, email.Date,email_attach.Attach_File_Name,email_attach.Attachments_Route from email,email_attach where email.ID=email_attach.ID and Attach_File_Name like "%s"'''%(sqlfilename+'%')
    cur.execute(sql)
    column=list(cur.fetchall())
    column.insert(0,['ID','Subject','Date','Attach_File_Name','Attachments_Route'])
    print(tabulate(column))

    graph = nx.Graph()
    sql='''select email.Mail_From, email_To.Mail_To, email.Subject, email.Date, email_attach.Attach_File_Name from email left join email_To on email.ID=email_To.ID left join email_attach on email_To.Id=email_attach.ID where Attach_File_Name like "%s"'''%(sqlfilename+'%') +"""order by Date;"""
    cur.execute(sql)
    column = list(cur.fetchall())
    count = 2
    temp_column = []
    for i in range(0, len(column)):
        if not column[i] == temp_column:
            temp_column = column[i]
            graph.add_edge(str(count - 1) + '. ' + column[i][0], str(count) + '. ' + column[i][1],filename=column[i][4])
            count += 1
        else:
            continue

    plt.figure('%s Filename Search result Visualize' % filename, figsize=((len(column)+2), (len(column))+2))
    pos = nx.spring_layout(graph)
    #labels = nx.get_edge_attributes(graph)
    #nx.draw_networkx_edge_labels(graph, pos,font_family=font_name,font_size=10)
    nx.draw(graph, pos, with_labels=True)
    labels = nx.get_edge_attributes(graph, 'filename')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels,font_family=font_name,font_size=10)
    plt.margins(x=0.4, y=0.4)
    plt.savefig('%s Filename Search result Visualize.png' % filename, bbox_inches='tight')

def MailAddress_to(address):
    db = pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()
    sql = '''select email.ID,email_To.Mail_To,email.Mail_From,email.Subject,email_attach.Attach_File_Name, email.Date from email join email_To on (email.ID=email_To.ID and email_To.Mail_To='%s') join email_attach on email_To.Id=email_attach.ID''' % address
    cur.execute(sql)

    column = list(cur.fetchall())
    column.insert(0, ['ID', 'Mail_To', 'Mail_From', 'Subject', 'Attach_File_Name','Date'])
    print(tabulate(column))

def MailAddress_from(address):
    db = pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()
    sql = '''select email.ID,email_To.Mail_To,email.Mail_From,email.Subject,email_attach.Attach_File_Name, email.Date from email join email_To on (email.ID=email_To.ID and email.Mail_From='%s') join email_attach on email_To.Id=email_attach.ID''' % address
    cur.execute(sql)

    column = list(cur.fetchall())
    column.insert(0, ['ID', 'Mail_To', 'Mail_From', 'Subject', 'Attach_File_Name', 'Date'])
    print(tabulate(column))

def MailAddress_tofrom(to_address,from_address):
    db = pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()
    sql = '''select email.ID,email_To.Mail_To,email.Mail_From,email.Subject,email_attach.Attach_File_Name, email.Date from email join email_To on (email.ID=email_To.ID and email_To.Mail_To='%s' and email.Mail_From='%s') join email_attach on email_To.Id=email_attach.ID''' % (to_address,from_address)
    cur.execute(sql)

    column = list(cur.fetchall())
    column.insert(0, ['ID', 'Mail_To', 'Mail_From', 'Subject', 'Attach_File_Name', 'Date'])
    print(tabulate(column))

def Search_Body(id):
    db = pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()
    sql = '''select Date,Body from email where ID=%d'''%int(id)
    cur.execute(sql)

    column = list(cur.fetchall())
    column.insert(0, ['Date','Body'])
    print(tabulate(column))

def Search_Date(datetime):
    db = pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()
    sql = """select email.ID, email.Date, email.Subject, email_To.Mail_To, email.Mail_From from email, email_To where email.ID=email_To.ID and date_format(Date,'%Y-%m-%d')="""
    sql+="'"+datetime+"'"
    cur.execute(sql)
    column = list(cur.fetchall())
    column.insert(0, ['ID', 'Date','Subject','Mail_To','Mail_From'])
    print(tabulate(column))

def User_Input(sql):
    db = pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()
    if sql.startswith('select') and not sql.find('create') and not sql.find('insert') and not sql.find('update') and not sql.find('drop') and not sql.find('delete') and not sql.find('alter') :
        cur.execute(sql)
        column = list(cur.fetchall())
        print(tabulate(column))
    else:
        print('Not Acceptable Query')
        return

def Keyword_Search(keyword):
    db = pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()
    sql="""select email.ID,email_To.Mail_To,email.Mail_From,email.Subject,email_attach.Attach_File_Name, email.Date from email left join email_To on email.ID=email_To.ID left join email_attach on email_To.Id=email_attach.ID where match(Subject,Body) against('%s') order by Date;"""%keyword
    cur.execute(sql)
    column = list(cur.fetchall())
    column.insert(0, ['ID', 'Mail_To', 'Mail_From', 'Subject', 'Attach_File_Name', 'Date'])
    print(tabulate(column))

    graph = nx.Graph()
    sql="""select email.Mail_From,email_To.Mail_To,email.Subject,email_attach.Attach_File_Name, email.Date from email left join email_To on email.ID=email_To.ID left join email_attach on email_To.Id=email_attach.ID where match(Subject,Body) against('%s') order by Date;"""%keyword
    cur.execute(sql)
    column = list(cur.fetchall())
    count=2
    temp_column=[]
    for i in range(0,len(column)):
        if not column[i]==temp_column:
            temp_column=column[i]
            graph.add_edge(str(count-1)+'. '+column[i][0], str(count)+'. '+column[i][1])
            count+=1
        else:
            continue

    plt.figure('%s Keyword Search result Visualize' % keyword, figsize=(len(column), len(column)))
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True)

    plt.margins(x=0.4, y=0.4)
    plt.savefig('%s Keyword Search result Visualize.png' % keyword, bbox_inches='tight')

def Frequency_MonthVisualize(input_address,input_dateYM):
    #input_date='2020-09'
    #input_address='phj971002@gmail.com'

    mail_count =[]

    db = pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()

    for i in range(1,32):
        sql = """select count(email.ID) from email where email.Mail_From='%s'"""%input_address + """ and date_format(Date,"%Y-%m-%d")="""
        sql2= """select count(email.ID) from email,email_To where email.ID=email_To.ID and email_To.Mail_To='%s'"""%input_address + """ and date_format(Date,"%Y-%m-%d")="""
        stri=str(i)
        if i<10:
            stri='0'+stri
        sql += "'" + input_dateYM + '-'+stri+"'"
        sql2 += "'" + input_dateYM + '-' + stri + "'"
        cur.execute(sql)
        count=cur.fetchone()[0]
        cur.execute(sql2)
        count += cur.fetchone()[0]
        mail_count.append(count)

    plt.figure(figsize=(12, 7))
    plt.grid(True, axis='y')
    plt.plot(mail_count, color="skyblue", marker='o')
    plt.xticks(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
         30],
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
         '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31'])
    plt.ylim(0, max(mail_count)+math.ceil(max(mail_count)*0.1))
    plt.xlabel('Day',fontsize=14)
    plt.ylabel('Comunication Count',fontsize=14)
    plt.title('%s Month E-mail Frequency Analysis'% input_dateYM,fontsize=14)
    plt.legend(['%s'%input_address])
    #plt.show()
    plt.savefig("%s Month_Visualize"%input_dateYM + ".png", bbox_inches='tight')

def Frequency_DateVisualize(input_address,input_dateYMD):
    #input_address='phj971002@daum.net'
    #input_dateYMD='2020-09-26'
    mail_count=[]
    mail_list=[]
    db = pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()

    sql = """select email_To.Mail_To from email, email_To where email.ID=email_To.ID and email.Mail_From='%s'""" % input_address + """ and date_format(Date,"%Y-%m-%d")="""
    sql += "'"+input_dateYMD+"'"
    cur.execute(sql)
    maillist = cur.fetchall()
    maillist = list(set(list(maillist)))

    for i in range(0,len(maillist)):
        sql = """select count(email_To.Mail_To) from email, email_To where email.ID=email_To.ID and email.Mail_From='%s' and email_To.Mail_To='%s'""" % (maillist[i][0],input_address)+"""and date_format(Date,"%Y-%m-%d")="""
        sql += "'" + input_dateYMD + "'"
        cur.execute(sql)
        size=cur.fetchone()[0]
        sql = """select count(email_To.Mail_To) from email, email_To where email.ID=email_To.ID and email.Mail_From='%s' and email_To.Mail_To='%s'""" % (
        input_address, maillist[i][0]) + """and date_format(Date,"%Y-%m-%d")="""
        sql += "'" + input_dateYMD + "'"
        cur.execute(sql)
        size += cur.fetchone()[0]
        mail_count.append(size)
        mail_list.append(maillist[i][0])
    plt.figure(figsize=(12, 7))
    plt.grid(True, axis='y')
    plt.bar(mail_list,mail_count, color="skyblue")
    plt.xticks(range(len(maillist)), mail_list)
    #plt.ylim(0, max(mail_count) + math.ceil(max(mail_count) * 0.1))
    plt.xlabel('Mail Address',fontsize=14)
    plt.ylabel('Comunication Count',fontsize=14)
    plt.title("%s %s_Visualize" % (input_dateYMD,input_address),fontsize=14)
    plt.legend(['%s' % input_address])
    # plt.show()
    plt.savefig("%s %s_Visualize" % (input_dateYMD,input_address) + ".png", bbox_inches='tight')

def Frequency_HeatmapVisualize(input_dateYMD):
    #보낸거만 카운트
    input_dateYMD='2020-09-26'
    employee = ['phj971002@gmail.com', 'hjp971002@naver.com', 'phj971002@daum.net', 'phj100297@naver.com']

    db = pymysql.connect(host='218.146.20.50', user='hadoopuser', password='Hadoopuser1!', db='case1', charset='utf8')
    cur = db.cursor()
    date_count = []
    mail_address = []
    for i in range(0,len(employee)):
        temp_count = [0 for i in range(24)]
        sql="""select hour(email.Date) from email,email_To where email.ID=email_To.ID and email.Mail_From='%s';"""%employee[i]
        cur.execute(sql)
        sql_count=list(cur.fetchall())
        for j in range(0,len(sql_count)):
            temp_count[sql_count[j][0]]+=1
        date_count.append(temp_count)
        mail_address.append(employee[i])

    df = pd.DataFrame(data=np.array(date_count),index=mail_address,columns=list(range(0,24)))
    plt.figure(figsize=(16, len(mail_address)+1))
    ax=sns.heatmap(df, cmap='Blues',linewidths=0.3, annot=False, fmt='d')
    plt.title('%s Mail Send Count'%input_dateYMD, fontsize=14)
    plt.xlabel('Time of Date', fontsize=14)
    plt.ylabel('Mail Address', fontsize=14)
    plt.savefig("%s Mail Send Count" % (input_dateYMD) + ".png", bbox_inches='tight')




if __name__ == '__main__':
    input_value=sys.argv
    select_value=len(input_value)

    '''
    argv[1] 숫자, argv[2,3] 입력 값
    1 : 첨부파일 리스트, 2 : 특정 첨부파일 조회, 3 : To 값 입력, 4 : From 값 입력, 5 : To, From 입력 6: Body 조회, 7: Date 조회, 8: SQL 사용자 입력, 9: keyword search, 10: 월별 빈도분석
    
    '''
    '''
    try:
        if input_value[1]=='1':
            Attach_list()
        elif input_value[1]=='2':
            Attach_find(input_value[2])
        elif input_value[1]=='3':
            MailAddress_to(input_value[2])
        elif input_value[1]=='4':
            MailAddress_from(input_value[2])
        elif input_value[1] == '5':
            MailAddress_tofrom(input_value[2],input_value[3])
        elif input_value[1] == '6':
            Search_Body(input_value[2])
        elif input_value[1] == '7':
            Search_Date(input_value[2])
        elif input_value[1] == '8':
            User_Input(input_value[2])
        elif input_value[1] == '9':
            User_Input(input_value[2])
        else:
            print('Unknown Input')
    except:
        print("Input error")
    '''
    #user_input(input_value[1], input_value[2])
    #visualize()




