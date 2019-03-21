# -*- coding: utf-8 -*-

from app import app
from flask import render_template




@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/index')
def index():
#    user = {'username': 'Miguel'}
    return render_template('index.html')