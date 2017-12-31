# TODO connect both

import twitter
import pymongo
import os
import sys
import time

from pymongo import MongoClient
client = MongoClient("mongodb://admin:password@ds235877.mlab.com:35877/scraperinvestment")
api = twitter.Api(consumer_key='yxf1KWz3TlFgOZmZ8lmWVslpv',
                  consumer_secret='PEv8G8oeTNF7DoeJKeMEcYomHZnYqr7jWLNR66t65MM0TKXoFG',
                  access_token_key='2792504612-L3dFWShNoQTkLczyaSlJWgk4zclTcxFdoZifQNi',
                  access_token_secret='c7FQyj8NeRjFgK5KBusmQoIvFRQyQkMsuwYHHNUMapw6j'
                  )
tweetsCollection = client.scraperinvestment.tweets
tweetCounts = client.scraperinvestment.tweetCounts

def postRandomTweets():
    for i in range(20):
        api.PostUpdate('Random Tweet number: ' + str(i))
    return

def listenForNewTweetsFrom(user):

    while True:
        print("Checking for new tweets from " + user)

        for i in range(10):
            time.sleep(1)
            progress(i+1,10)

        currentTweetCount = getCurrentTweetCountOf(user)
        savedTweetCount = getSavedTweetCountOf(user)
        
        print("\nsavedTweetCount: " + str(savedTweetCount))
        print("currentTweetCount: " + str(currentTweetCount))
        
        if int(currentTweetCount)>int(savedTweetCount):
            print("New tweets posted.... updating database")
            statuses = getLastTweetsOf(user,int(currentTweetCount) - int(savedTweetCount))
            populateDBWith(statuses, user)
            updateSavedTweetCountOf(user, currentTweetCount)

    return

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def populateDBWith(statuses, userhandle):
    currentStatus = 1
    totalStatuses = len(statuses)
    for status in statuses:
        tweetid = status.id_str
        timestamp = status.created_at
        text = status.text
        url = ""

        for eachurl in status.urls:
            url = eachurl.url

        progress(currentStatus, totalStatuses, status='Uploading Tweet Id: ' + tweetid)
        tweetsCollection.insert_one({
            'userhandle': userhandle,
            'tweetid' : tweetid,
            'timestamp': timestamp,
            'text': text,
            'url': url
            })
        currentStatus += 1

    print("\nDb Populated")
    return

def getLastTweetsOf(user, n):
    if(n>200):
        print("requested tweet number too big, defaulting to max of 200")
        n = 200

    print("Getting last "+ str(n) + " tweets (and ignoring replies)")
    statuses = api.GetUserTimeline(
        screen_name = user, 
        count = n, 
        trim_user = True, 
        exclude_replies = True
        )
    print("Done")
    return statuses

def getCurrentTweetCountOf(user):
    return api.GetUser(screen_name = user).statuses_count

def getSavedTweetCountOf(user):
    result = tweetCounts.find_one({
        'userhandle': user
        })
    if(result != None):
        return result['tweetCount']
    else: 
        return 0

def updateSavedTweetCountOf(user, count):
    tweetCounts.update_one({
        'userhandle': user,
        },{
        '$set': {'tweetCount': count}
        }, upsert = True)

def main():
    listenForNewTweetsFrom("asymmetricalpha")
    return


if __name__ == "__main__":
    main()
