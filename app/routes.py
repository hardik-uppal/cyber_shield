# -*- coding: utf-8 -*-

from app import app
from flask import render_template,session,redirect,url_for
from flask import request
from apscheduler.schedulers.background import BackgroundScheduler
#import sqlite3
from TableScript import ExecuteReader
#import requests as rq
from GetCall import GetCall


@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/index', methods=['GET','POST'])
def index():
#    GetCall()
#    accessToken=ExtractToken()
#    endpointLink= "https://api.instagram.com/v1/users/self/media/recent?access_token={}".format(accessToken)
#    r = rq.get(endpointLink)
#    r = r.json()
#    user = r["data"][0]["user"]["full_name"]
#          
#    conn = sqlite3.connect('cyberShield.db')
#    c = conn.cursor()
#        
#    c.execute('INSERT INTO user VALUES (?,?)', user,accessToken)
#        
#    conn.commit()
#    conn.close()
          
    #chart1
    comment_count_chart1=[]
    users_chart1=[]
    dt_chart1=ExecuteReader("select count(*) as count,username from Comments Group by username order by count desc limit 5")
    for i in range(len(dt_chart1)):
        comment_count_chart1.append(dt_chart1[i][0])
        users_chart1.append(dt_chart1[i][1])
    
    #chart2
    comment_count_chart2=[0]*5
#    nlcLabel_chart2=[None]*5
    nlcLabel=['Identity Hate','Neutral', 'Obscene','Threat','Toxic']
    dt_chart2=ExecuteReader("select count(*) as count,NlcLabel from Comments Group by NlcLabel order by NlcLabel")
#    print(dt_chart2)
    for i in range(len(dt_chart2)):
#        comment_count_chart2.append(dt_chart2[i][0])
#        nlcLabel_chart2.append(dt_chart2[i][1])  
        for j in range(len(nlcLabel)):
            if nlcLabel[j].lower()==dt_chart2[i][1]:
                comment_count_chart2[j]=dt_chart2[i][0]

    #titlecount
    count_media_id=ExecuteReader("select count(distinct media_id) from Comments")
    explicit_comments=ExecuteReader("select count(*) from (select * from Comments where NlcLabel!='neutral' union select * from Comments where NlcLabel='neutral' and ToneLabel in ('Anger'))")
    total_comments=ExecuteReader("select count(distinct comments_id) from Comments")
    
    
    ##Comment table
    comment_text=[]
    commentTable=[]
    tone=[]
    nlc=[]
    user_table=[]
    dt_table1=ExecuteReader("select comment_text,username,NlcLabel,ToneLabel from (select * from Comments where NlcLabel!='neutral' union select * from Comments where NlcLabel='neutral' and ToneLabel in ('Anger'))")
    length_comment_table=len(dt_table1)
    for i in range(len(dt_table1)):
        commentTable.append([dt_table1[i][0],dt_table1[i][1],dt_table1[i][2],dt_table1[i][3]])
        comment_text.append(dt_table1[i][0])
        user_table.append(dt_table1[i][1])
        tone.append(dt_table1[i][2])
        nlc.append(dt_table1[i][3])


    ##graph 
    
    count_explicit_graph=[]
    date_graph=[]
    dt_graph=ExecuteReader("select count(*) as count,DATE(created_time, 'unixepoch') AS date from (select * from Comments where NlcLabel!='neutral' union select * from Comments where NlcLabel='neutral' and ToneLabel in ('Anger')) group by date")
    for i in range(len(dt_graph)):
        date_graph.append(dt_graph[i][1])
        count_explicit_graph.append(dt_graph[i][0])
        
    
    return render_template('index.html',users=users_chart1,commentTable=commentTable,length_comment_table=length_comment_table ,comment_count=comment_count_chart1,categories=nlcLabel,cat_comment_count=comment_count_chart2,count_explicit_graph=count_explicit_graph,date_graph=date_graph,count_media_id=count_media_id[0][0],explicit_comments=explicit_comments[0][0])

@app.route('/accessToken', methods=['GET','POST'])
def ExtractToken():
    if request.method == "POST":
        if request.form['token'] is not None:
            session['accessToken']=request.form['token']
            logfile=open('Log.txt','a')
            logfile.write(session['accessToken'])
            logfile.close()
            scheduler = BackgroundScheduler()
            scheduler.add_job(func=GetCall, trigger="interval", seconds=60)
            scheduler.start()
#            GetCall(session['accessToken'])
    return render_template('accessToken.html')

@app.route('/contactUs')
def contactUs():
    return render_template('contactUs.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')