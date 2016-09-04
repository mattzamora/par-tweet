import tweepy
import sqlite3

sqlite_file="~/TweetDB.sqlite"
#TODO set up consuer_key, consumer_secret, access_token, access_token_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()

conn.commit()
conn.close()

MIN_STATUSES = 1000
MIN_FOLLOWERS = 1000

results = api.search(q="Leg Workout")

for tweet in results:
    is_youtube_video = False
    is_sizeable = False
    statuses_count=tweet.user.statuses_count
    followers_count=tweet.user.followers_count

    if statuses_count > MIN_STATUSES and followers_count > MIN_FOLLOWERS:
        is_sizeable= True
        current_urls=tweet.entities['urls']
        if len(current_urls)>0:
            if u'expanded_url' in tweet.entities['urls'][0]:
                #print tweet.entities['urls'][0]['expanded_url']
                if "youtube.com" in tweet.entities['urls'][0]['expanded_url']:
                    is_youtube_video = True
                else:
                    print "Other url"
    
    if is_sizeable and is_youtube_video:
        api.retweet(tweet.id)
        
#print dir(results[0].user)
#print str(results[0].retweet_count)

#print results[0]
#print "followers_count: "+str(results[0].user.followers_count)
#print "following: "+str(results[0].user.followers_ids)
