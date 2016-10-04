import tweepy
import sqlite3
import os.path
import random

def setup(sqlite_file = "TweetDB.sqlite"):

    is_existing_db = os.path.isfile(sqlite_file)
    conn = sqlite3.connect(sqlite_file)  # Creates a new file if there is none, otherwise opens an existing file.
    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()

    if not is_existing_db:
        cursor.execute('''CREATE TABLE meta(consumer_key text, consumer_secret text, access_token text, access_token_secret text);''')

        cursor.execute(
            '''CREATE TABLE search_terms(search_term text);''')

        starting_terms=['Leg Workout','total body workout']

        for term in starting_terms:
            command="insert into search_terms(search_term) values('%s');"%(term)
            cursor.execute(command)

        keys_dict=load_external_api_keys()
        if not keys_dict:
            raise Exception('No valid keys are found in a secretkeys.dat file')
        else:
            consumer_key = keys_dict['consumer_key']
            consumer_secret = keys_dict['consumer_secret']
            access_token = keys_dict['access_token']
            access_token_secret = keys_dict['access_token_secret']

            cursor.execute("INSERT INTO meta(consumer_key, consumer_secret, access_token, access_token_secret) VALUES('%s','%s','%s','%s');"%(consumer_key, consumer_secret, access_token, access_token_secret))
    else:
        command="select * from meta;"
        a=cursor.execute(command)
        result=a.fetchone()

        consumer_key = result[0]
        consumer_secret = result[1]
        access_token = result[2]
        access_token_secret = result[3]

    api = load_api(consumer_key, consumer_secret, access_token, access_token_secret)

    return conn, cursor, api


def load_external_api_keys(secretkeys = "secretkeys.dat"):
    is_existing_keys_file = os.path.isfile(secretkeys)
    if is_existing_keys_file:
        keys = []
        with open(secretkeys) as f:
            for line in f:
                    keys.append(line.strip())
        keys_dict={}
        keys_dict['consumer_key'] = keys[0]
        keys_dict['consumer_secret'] = keys[1]
        keys_dict['access_token'] = keys[2]
        keys_dict['access_token_secret'] = keys[3]
    else:
        keys_dict = False

    return keys_dict


def load_api(consumer_key, consumer_secret, access_token, access_token_secret):

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    return api

def close(conn):
    conn.commit()
    conn.close()

def select_term(cursor):
    command="select * from search_terms;"
    results = cursor.execute(command)
    results = results.fetchall()
    result = random.choice(results)
    result = result[0]
    return result

def do_a_YouTube_Post(api, cursor):
    MIN_STATUSES = 1000
    MIN_FOLLOWERS = 1000

    search_term = select_term(cursor)

    results = api.search(q=search_term)

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
                    exanded_urls=tweet.entities['urls'][0]['expanded_url']
                    if "youtube.com" in exanded_urls or "youtu.be" in exanded_urls:
                        is_youtube_video = True
                    else:
                        print("Other url: "+str(tweet.entities['urls'][0]['expanded_url']))

        if is_sizeable and is_youtube_video:
            print("Initiating re-tweet")
            api.retweet(tweet.id)

    #print dir(results[0].user)
    #print str(results[0].retweet_count)

    #print results[0]
    #print "followers_count: "+str(results[0].user.followers_count)
    #print "following: "+str(results[0].user.followers_ids)


def follow_followers():
    for follower in tweepy.Cursor(api.followers).items():
        follower.follow()

if __name__=="__main__":
    conn, cursor, api =setup()
    if api!=False:
        print("Successful API Connection is "+str(api != False))
        do_a_YouTube_Post(api, cursor)
        follow_followers()
    else:
        raise Exception("API Connection is invalid")
    close(conn)