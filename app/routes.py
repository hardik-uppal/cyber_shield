# -*- coding: utf-8 -*-

from app import app
from flask import render_template

from TableScript import ExecuteReader


@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/index')
def index():

    comment_count_chart1=[]
    users_chart1=[]
    dt_chart1=ExecuteReader("select count(*) as count,username from Comments Group by username order by count desc limit 5")
    for i in range(len(dt_chart1)):
        comment_count_chart1.append(dt_chart1[i][0])
        users_chart1.append(dt_chart1[i][1])
    
    
    comment_count_chart2=[]
    nlcLabel_chart2=[]
    dt_chart2=ExecuteReader("select count(*) as count,NlcLabel from Comments Group by NlcLabel order by count desc")
    for i in range(len(dt_chart2)):
        comment_count_chart2.append(dt_chart2[i][0])
        nlcLabel_chart2.append(dt_chart2[i][1])  
    
    
    return render_template('index.html',users=users_chart1, comment_count=comment_count_chart1,categories=nlcLabel_chart2,cat_comment_count=comment_count_chart2)
