import numpy as np
import glob
from nltk.tokenize import word_tokenize
import sys
import tweepy
import json
import time
import os

tweet_limit = 899


def retrieve_tweet(twt_prop_path, twt_ids, outfile='./tweets_jhu.json'):
    """
    Retrieve tweets
    :param twt_prop_path dictionary of twitter authentication info
    :param twt_ids: list of tweet ids
    :return:
    """
    twt_prop = dict() # Twitter auth properties
    try:
        twt_prop = json.load(open(twt_prop_path))
    except:
        print('Authentication file loading fail')
        sys.exit()

    auth = tweepy.OAuthHandler(twt_prop['api_key'], twt_prop['api_secret'])
    auth.set_access_token(twt_prop['access_token'], twt_prop['access_secret'])
    twt_api = tweepy.API(auth)

    global tweet_limit # the limit of request per 15 minutes
    """
        count and error_count record the number of tweets can be retrieved and unreachable

        The script supports continuous scraping through the finished_set and the finished_tmp file;
        If the id exists in the finished_tmp file, it will not be requested again.
    """
    finished_set = set()
    count = 0
    error_count = 0

    if os.path.isfile('./finished_tmp.txt'):
        finished_file = open('./finished_tmp.txt', 'a')
        with open('./finished_tmp.txt') as tmp_file:
            [finished_set.add(item.strip()) for item in tmp_file]
    else:
        finished_file = open('./finished_tmp.txt', 'w')

    if os.path.isfile(outfile):
        with open(outfile) as tmpfile:
            [finished_set.add(item.strip()) for item in tmpfile]
        writefile = open(outfile, 'a')
    else:
        writefile = open(outfile, 'w')

    for tid in twt_ids:
        if str(tid) in finished_set:
            continue

        try:
            #print('id'+str(tid))
            tweet = twt_api.get_status(tid)
            print(tweet)
            writefile.write(json.dumps(tweet._json)+'\n')
            finished_set.add(tid)
        except tweepy.TweepError as te:
            #print(te)
            error_count += 1
        finished_file.write(str(tid)+'\n')
        finished_set.add(str(tid))
        count += 1
        if count % 100 == 0:
            writefile.flush()
            finished_file.flush()

        if count >= tweet_limit:
            count -= tweet_limit
            time.sleep(60*15) # suspend for 15 minutes

    writefile.flush()
    writefile.close()
    os.remove('./finished_tmp.txt')

# scann the files within the current dir, the files contains Tweet IDs
work_dir = './'
save_dir = './'
if len(sys.argv) > 1:
    if os.path.exists(sys.argv[1]):
        work_dir = sys.argv[1]
    if os.path.exists(sys.argv[2]):
        save_dir = sys.argv[2]
    if not work_dir.endswith('/'):
        work_dir += '/'
    if not save_dir.endswith('/'):
        save_dir += '/'

files = glob.glob(work_dir + '*.txt') # you can also specify other directories
#print(files)
time.sleep(10)
for filepath in files:
    twids = open(filepath).readlines()
    twids = [item.split('\t')[0].strip() for item in twids]

    #print('Working on: ' + filepath)
    retrieve_tweet('./twitter.info', twids, outfile='./tweets_jhu.json')
