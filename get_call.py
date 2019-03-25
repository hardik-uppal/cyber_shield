import requests as rq
from TableScript import InsertTable,getRecentDate
from apiTest import apiNLCTest 
from apiTest import apiToneTest


endpointLink= "https://api.instagram.com/v1/users/self/media/recent?access_token=11639557926.5d4680b.faec56455bd04f7ab2389f26c17cbb01"

#endpointLink1="https://api.instagram.com/v1/media/1998460770850257087_11639557926/comments?access_token=11639557926.7897a2c.127898c631cd41a3b4300e1e29d560d3"
r = rq.get(endpointLink)
r = r.json()
#print(len(r))
#data = json.loads(r.text)
#for t in r:
#    print(t)
media_id_list=[]
for ids in range(len(r["data"])):
    media_id_list.append(r["data"][ids]["id"])




comments=[]
for i in range(len(media_id_list)):
    comments_data=(rq.get("https://api.instagram.com/v1/media/{}/comments?access_token=11639557926.5d4680b.faec56455bd04f7ab2389f26c17cbb01".format(media_id_list[i]))).json()
#    print(media_id_list[i],len(comments_data["data"]))
    for j in range(len(comments_data["data"])):
#        comments_temp.append(comments_data["data"][j])
#        print(comments_data["data"][j],"___________")
#        print(comments_data["data"][j]["text"],apiToneTest(comments_data["data"][j]["text"])[1])
        media_id,comments_id, username, comment_text, created_time, NlcLabel, ToneLabel = media_id_list[i],comments_data["data"][j]["id"],comments_data["data"][j]["from"]["username"],comments_data["data"][j]["text"],comments_data["data"][j]["created_time"],apiNLCTest(comments_data["data"][j]["text"])[0],apiToneTest(comments_data["data"][j]["text"])[1]
##        print(media_id,comments_id, username, comment_text, created_time)
        comments.append([media_id,comments_id, username, comment_text, created_time, NlcLabel, ToneLabel])
#print((comments))
for i in range(len(comments)): 

    if(int(comments[i][4]) > getRecentDate()[0]):
        InsertTable(comments[i])
        print('Inserted')
    else:
        print('already present')

    
