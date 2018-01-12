# TODO connect both

import twitter
import pymongo
import os
import sys
import time
import logging
import argparse

from pymongo import MongoClient
client = MongoClient("mongodb://admin:password@ds235877.mlab.com:35877/scraperinvestment")
api = twitter.Api(consumer_key='yxf1KWz3TlFgOZmZ8lmWVslpv',
                  consumer_secret='PEv8G8oeTNF7DoeJKeMEcYomHZnYqr7jWLNR66t65MM0TKXoFG',
                  access_token_key='2792504612-L3dFWShNoQTkLczyaSlJWgk4zclTcxFdoZifQNi',
                  access_token_secret='c7FQyj8NeRjFgK5KBusmQoIvFRQyQkMsuwYHHNUMapw6j'
                  )
tweetsCollection = client.scraperinvestment.tweets
tweetCounts = client.scraperinvestment.tweetCounts

disableProgressBar = False

def postRandomTweets():
    for i in range(20):
        api.PostUpdate('Random Tweet number: ' + str(i))
    return

def listenForNewTweetsFrom(user, updateFrequency):

    while True:
        logging.info("Checking for new tweets from " + user)

        # print("updating....")
        for i in range(updateFrequency):
            time.sleep(1)
            progress(i+1,updateFrequency)

        currentTweetCount = getCurrentTweetCountOf(user)
        savedTweetCount = getSavedTweetCountOf(user)
        
        logging.info("savedTweetCount: " + str(savedTweetCount))
        logging.info("currentTweetCount: " + str(currentTweetCount))
        
        if int(currentTweetCount)>int(savedTweetCount):
            logging.info("New tweets posted.... updating database")
            statuses = getLastTweetsOf(user,int(currentTweetCount) - int(savedTweetCount))
            populateDBWith(statuses, user)
            updateSavedTweetCountOf(user, currentTweetCount)

        elif int(currentTweetCount)<int(savedTweetCount):
            # print("New tweets less than saved, something weird happened.... adding last few tweets while ignoring duplicates")
            logging.info("New tweets less than saved, something weird happened.... adding last few tweets while ignoring duplicates")     
            statuses = getLastTweetsOf(user,200)
            updateSavedTweetCountOf(user, currentTweetCount)
            for eachTweet in statuses:
                if tweetIsAlreadyInDb(eachTweet):
                    # print(eachTweet.id_str + " is already in db, skipping...")
                    logging.info(eachTweet.id_str + " is already in db, skipping...")
                    continue
                else: 
                    # print("adding tweet with id: " + eachTweet.id_str + " to DB")
                    logging.info("adding tweet with id: " + eachTweet.id_str + " to DB")
                    populateDBWith([eachTweet],user)

        else:
            continue

    return

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    if(disableProgressBar == False):
        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
        sys.stdout.flush()

def tweetIsAlreadyInDb(tweet):
    return tweetsCollection.find_one({'tweetid' : tweet.id_str}) != None

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

    logging.info("\nDb Populated")
    return

def getLastTweetsOf(user, n):
    if(n>200):
        logging.info("requested tweet number too big, defaulting to max of 200")
        n = 200

    logging.info("Getting last "+ str(n) + " tweets (and ignoring replies)")
    statuses = api.GetUserTimeline(
        screen_name = user, 
        count = n, 
        trim_user = True, 
        exclude_replies = True
        )
    logging.info("Done")
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

def isValidUser(user):
    try:
        api.GetUser(screen_name = user)
        return True
    except Exception, e:    
        return False

def convertlevel(level_as_string):
    if level_as_string == "info":
        return logging.INFO
    elif level_as_string == "debug":
        return logging.DEBUG
    elif level_as_string == "error":
        return logging.ERROR
    else:
        # print("invalid log level specified")
        exit()
        return 0

def main():

    print("Starting script")

    parser = argparse.ArgumentParser()
    parser.add_argument("user", help = "Define user to log tweets")
    parser.add_argument("-f", "--updatefrequency" , help = "Set update frequency (default 10 sec)", default = 10, type = int)
    parser.add_argument("-nb", "--nobar" , help = "disable timer bar between updates", action = "store_true")
    parser.add_argument("-l", "--log", help = "log update request", default = "error")
    args = parser.parse_args()
    
    requestedUser = args.user
    updateFrequency = args.updatefrequency

    global disableProgressBar 
    disableProgressBar = args.nobar

    logging.basicConfig(filename= requestedUser + "_output.log",level=convertlevel(args.log))

    if(isValidUser(requestedUser)):
        logging.critical("User " + requestedUser + " valid") 
        print("user twitter stream now being logged")
        listenForNewTweetsFrom(requestedUser, updateFrequency)
    else: 
        print("invalid user " + requestedUser + " specified, please re-run script with valid user")
        logging.error("invalid user " + requestedUser + " specified, please re-run script with valid user")
    return


if __name__ == "__main__":
    main()
