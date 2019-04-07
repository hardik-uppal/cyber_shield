import requests as rq
from TableScript import InsertTable,getRecentDate,checkComment
from apiTest import apiNLCTest 
from apiTest import apiToneTest
import os


def GetCall(accessToken):
    filePath="Log.txt"
    accessToken=accessToken.rstrip(',')
    # API endpoint url to fetch user comments from instagram
    endpointLink= "https://api.instagram.com/v1/users/self/media/recent?access_token={}".format(accessToken)
    if os.path.exists(filePath):
        os.remove(filePath)
        logfile=open('Log.txt','a')
        logfile.write('previous log file deleted')
        logfile.close()
    else:
        
        logfile=open('Log.txt','a')
        logfile.write('Can not delete the file as it does not exists\n')
        logfile.close()
    # API call to get user details as json
    r = rq.get(endpointLink)
    r = r.json()
    # extracting user name from json
    main_user = r["data"][0]["user"]["full_name"]

    logfile=open('Log.txt','a')
    logfile.write('json present')
    logfile.close()
    while r is None:
        logfile=open('Log.txt','a')
        logfile.write('waiting for json\n')
        logfile.close()
    # fetching media/posts details from json
    if r is not None:
        media_id_list=[]
        for ids in range(len(r['data'])):
            media_id_list.append(r['data'][ids]['id'])
            logfile=open('Log.txt','a')
            logfile.write('media list inserted\n')
            logfile.close()
    else:
        media_id_list=[]
    # fetching comments from media details and calling NLC classifier test method to extract explicit comments
    comments=[]
    if len(media_id_list)!=0:
        
        for i in range(len(media_id_list)):
            comments_data=(rq.get("https://api.instagram.com/v1/media/{0}/comments?access_token={1}".format(media_id_list[i],accessToken))).json()
            for j in range(len(comments_data['data'])):
                media_id,comments_id, username, comment_text, created_time, NlcLabel, ToneLabel = media_id_list[i],comments_data["data"][j]["id"],comments_data["data"][j]["from"]["username"],comments_data["data"][j]["text"],comments_data["data"][j]["created_time"],apiNLCTest(comments_data["data"][j]["text"])[0][0],apiToneTest(comments_data["data"][j]["text"])[1]

                comments.append([media_id,comments_id, username, comment_text, created_time, NlcLabel, ToneLabel])
        
        logfile=open('Log.txt','a')
        logfile.write('Comment list inserted')
        logfile.close()
    else:
        comments=[]
    # populating DB with explicit comments only
    if len(comments)!=0:
        for i in range(len(comments)): 
            if checkComment(int(comments[i][1])) is None:
                InsertTable(comments[i])
                logfile=open('Log.txt','a')
                logfile.write('Inserted\n')
                logfile.close()
            else:
                logfile=open('Log.txt','a')
                logfile.write('already present\n')
                logfile.close()
    return main_user
