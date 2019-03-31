# -*- coding: utf-8 -*-

from app import app
from flask import render_template,session,redirect,url_for,jsonify
from flask import request
from apscheduler.schedulers.background import BackgroundScheduler
#import sqlite3
from TableScript import ExecuteReader
#import requests as rq
from GetCall import GetCall
import os
from watson_developer_cloud import NaturalLanguageClassifierV1


@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/index', methods=['GET','POST'])
def index():
    accessToken=session.get("accessToken")
#    if 'accessToken' in session:
    logfile=open('routesLog.txt','a')
    logfile.write("session value:{0}".format(accessToken))
    logfile.close()  
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
        
    main_user = session.get('main_user', None)
    return render_template('index.html',main_user=main_user,option_list=comment_text,users=users_chart1,commentTable=commentTable,length_comment_table=length_comment_table ,comment_count=comment_count_chart1,categories=nlcLabel,cat_comment_count=comment_count_chart2,count_explicit_graph=count_explicit_graph,date_graph=date_graph,count_media_id=count_media_id[0][0],explicit_comments=explicit_comments[0][0])
#    else:
#        return redirect(url_for("login"))
@app.route('/accessToken', methods=['GET','POST'])
def ExtractToken():
    if request.method == "POST":
        if request.form['token'] is not None:
            accessToken=request.form['token']

            filePath = 'routesLog.txt';
         
            # As file at filePath is deleted now, so we should check if file exists or not not before deleting them
            if os.path.exists(filePath):
                os.remove(filePath)
                logfile=open('routesLog.txt','a')
                logfile.write('previous log file deleted')
                logfile.close()
            else:
                
                logfile=open('routesLog.txt','a')
                logfile.write('Can not delete the file as it does not exists\n')
                logfile.close()
            
            while accessToken is None:
                logfile=open('routesLog.txt','a')
                logfile.write('waiting for access token')
                logfile.close()
            session['accessToken']=accessToken
            main_user=GetCall(accessToken)
            session['main_user']=main_user
            
            scheduler = BackgroundScheduler()
            scheduler.add_job(lambda: GetCall(accessToken), trigger="interval", seconds=30)
            scheduler.start()
#            GetCall(session['accessToken'])
    return render_template('accessToken.html')

@app.route('/analyze', methods=['GET', 'POST'])
def Analyze():
    api_key="LiI3o53WHaOU02ATKIwKhSQdirvntK1lZUPA6rhdEwCZ"
    workspace_ID="6deb62x509-nlc-477"
    natural_language_classifier = NaturalLanguageClassifierV1(iam_apikey=api_key)
    comment_text = request.form['text']
    classes = {}
    result = ""
    if comment_text != "":
        classes = natural_language_classifier.classify(workspace_ID, comment_text)
    result = classes.result
    return jsonify(result)

@app.route('/contactUs')
def contactUs():
    return render_template('contactUs.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')