# -*- coding: utf-8 -*-

from app import app
from flask import render_template,session,redirect,url_for,jsonify
from flask import request
from apscheduler.schedulers.background import BackgroundScheduler
from TableScript import ExecuteReader
from GetCall import GetCall
import os
from watson_developer_cloud import NaturalLanguageClassifierV1
import requests as rq

# login page
@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

# dashboard page
@app.route('/index', methods=['GET','POST'])
def index():
    
    f = open("accessToken.txt", "r")
    tempList = f.readline().split(',')
    accessToken = tempList[0]
    main_user = tempList[1]

    if accessToken:
        comment_count_chart1 = []
        users_chart1 = []
        # bar chart
        dt_chart1 = ExecuteReader("select count(*) as count,username from Comments Group by username order by count desc limit 5")
        for i in range(len(dt_chart1)):
            comment_count_chart1.append(dt_chart1[i][0])
            users_chart1.append(dt_chart1[i][1])
        
        # pie chart
        comment_count_chart2=[0]*5
        nlcLabel = ['Identity Hate','Neutral', 'Obscene','Threat','Toxic']
        dt_chart2 = ExecuteReader("select count(*) as count,NlcLabel from Comments Group by NlcLabel order by NlcLabel")

        for i in range(len(dt_chart2)):
            for j in range(len(nlcLabel)):
                if nlcLabel[j].lower()==dt_chart2[i][1]:
                    comment_count_chart2[j]=dt_chart2[i][0]
    
        # title count
        count_media_id=ExecuteReader("select count(distinct media_id) from Comments")
        explicit_comments=ExecuteReader("select count(*) from (select * from Comments where NlcLabel!='neutral' union select * from Comments where NlcLabel='neutral' and ToneLabel in ('Anger'))")

        # comment table
        comment_text = []
        commentTable = []
        tone = []
        nlc = []
        user_table = []
        dt_table1 = ExecuteReader("select comment_text,username,NlcLabel,ToneLabel,DATETIME(created_time, 'unixepoch') AS date from (select * from Comments where NlcLabel!='neutral' union select * from Comments where NlcLabel='neutral' and ToneLabel in ('Anger'))")
        length_comment_table = len(dt_table1)
        for i in range(len(dt_table1)):
            commentTable.append([dt_table1[i][0],dt_table1[i][1],dt_table1[i][2],dt_table1[i][3],dt_table1[i][4]])
            comment_text.append(dt_table1[i][0])
            user_table.append(dt_table1[i][1])
            tone.append(dt_table1[i][2])
            nlc.append(dt_table1[i][3])

        # trend area graph
        
        count_explicit_graph = []
        date_graph = []
        dt_graph = ExecuteReader("select count(*) as count,DATE(created_time, 'unixepoch') AS date from (select * from Comments where NlcLabel!='neutral' union select * from Comments where NlcLabel='neutral' and ToneLabel in ('Anger')) group by date")
        for i in range(len(dt_graph)):
            date_graph.append(dt_graph[i][1])
            count_explicit_graph.append(dt_graph[i][0])

        return render_template('index.html',main_user=main_user,option_list=comment_text,users=users_chart1,commentTable=commentTable,length_comment_table=length_comment_table ,comment_count=comment_count_chart1,categories=nlcLabel,cat_comment_count=comment_count_chart2,count_explicit_graph=count_explicit_graph,date_graph=date_graph,count_media_id=count_media_id[0][0],explicit_comments=explicit_comments[0][0])
    else:
        return redirect(url_for("login"))

# intermediate page to fetch access token
@app.route('/accessToken', methods=['GET','POST'])
def ExtractToken():
    if request.method == "POST":
        if request.form['token'] is not None:
            accessToken = request.form['token']
            while accessToken is None:
                logfile = open('routesLog.txt','a')
                logfile.write('waiting for access token')
                logfile.close()
            filePath = 'accessToken.txt';
            if os.path.exists(filePath):
                os.remove(filePath)

            accessToken1 = accessToken.rstrip(',')
            endpointLink = "https://api.instagram.com/v1/users/self/media/recent?access_token={}".format(accessToken1)
            r = rq.get(endpointLink)
            r = r.json()
            # storing access token and username in a temporary file
            main_user = r["data"][0]["user"]["full_name"]
            logfile = open('accessToken.txt','w+')
            logfile.write("{0}{1}".format(accessToken,main_user))
            logfile.close()
            # getCall populates DB with all the comments from instagram and assign labels
            GetCall(accessToken)
            # initialize scheduler for every 30 sec to call GetCall method
            scheduler = BackgroundScheduler()
            scheduler.add_job(lambda: GetCall(accessToken), trigger="interval", seconds=30)
            scheduler.start()
    return render_template('accessToken.html')

# method to analyze a random comment
@app.route('/analyze', methods=['GET', 'POST'])
def Analyze():
    api_key = "LiI3o53WHaOU02ATKIwKhSQdirvntK1lZUPA6rhdEwCZ"
    workspace_ID = "6deb62x509-nlc-477"
    natural_language_classifier = NaturalLanguageClassifierV1(iam_apikey=api_key)
    comment_text = request.form['text']
    classes = {}
    result = ""
    if comment_text != "":
        classes = natural_language_classifier.classify(workspace_ID, comment_text)
    result = classes.result
    return jsonify(result)

# contact us page
@app.route('/contactUs')
def contactUs():
    f = open("accessToken.txt", "r")
    tempList = f.readline().split(',')
    main_user = tempList[1]
    return render_template('contactUs.html',main_user=main_user)

# FAQ page
@app.route('/faq')
def faq():
    f = open("accessToken.txt", "r")
    tempList = f.readline().split(',')
    main_user = tempList[1]
    return render_template('faq.html',main_user=main_user)


# logout
@app.route('/logout')
def logout():
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)