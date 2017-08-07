import tweepy
import os
import csv
import json
# Twitter API credentials
cfg = {
   "consumer_key"        : "",
   "consumer_secret"     : "",
   "access_token"        : "",
   "access_token_secret" : ""
   }

apilist=[]
accselect=0

def get_api(cfg):
    #Twitter only allows access to a users most recent 3240 tweets with this method

    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    return tweepy.API(auth)

def get_all_tweets(screen_name):
    api = get_api(apilist[accselect])

    #initialize a list to hold all the tweepy Tweets
    alltweets = []

    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name, count = 200)

    #save most recent tweets
    alltweets.extend(new_tweets)

    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print("getting tweets before {}".format(oldest))

        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name, count = 200, max_id = oldest)

        #save most recent tweets
        for tweet in new_tweets:
            alltweets.append(tweet)
        
        #stop condition
        if alltweets[-1].id -1 == oldest:
            break
        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print("...{} tweets downloaded so far".format(len(alltweets)))

    # transform the tweepy tweets into a 2D array that will populate the csv
    outtweets=[] 
    for tweet in alltweets:
        outtweets.append([tweet.id_str,tweet.created_at,tweet.text.encode("utf-8")])

    # write to csv
    with open('{}_tweets.csv'.format(screen_name),'w') as f:
        writer = csv.writer(f)
        writer.writerow(["id","created_at","text"])
        writer.writerows(outtweets)

    pass

def readjson():
    accfile='./accts.json'
    try:
        with open(accfile, 'r') as account_data:
            d = json.load(account_data)
            for item in d:
                duplicate=0
                for api in apilist:
                    if(api["consumer_key"] == item["consumer_key"] and api["consumer_secret"] == item["consumer_secret"] and api["access_token"] == item["access_token"] and api["access_token_secret"] == item["access_token_secret"]):
                        duplicate=1
                if(duplicate==0):
                    apilist.append(item)
                else:
                    print("Duplicate Account Read & Ignored")
    except:
        print("No json Account file found.")

def writejson():
    with open("./accts.json", "w") as outfile:
        json.dump(apilist, outfile)

def initaccs():
    readjson()
    path='./input/'
    namearray=[]
    try:
        for filename in os.listdir(path):
            namearray.append(path+filename)
        for name in namearray:
            try:
                f = open(name)
        
                store = {}
                store["acc_name"]=name[8:] #removes directory preamble
                store["consumer_key"]=f.readline()[:-1] #removes the \n
                store["consumer_secret"]=f.readline()[:-1]
                store["access_token"]=f.readline()[:-1]
                store["access_token_secret"]=f.readline()[:-1]
                duplicate=0
                for api in apilist:
                    if(api["consumer_key"] == store["consumer_key"] and api["consumer_secret"] == store["consumer_secret"] and api["access_token"] == store["access_token"] and api["access_token_secret"] == store["access_token_secret"]):
                    #if(api["consumer_key"] == store["consumer_key"]):
                        duplicate=1
                if(duplicate==0):
                    apilist.append(store)
                else:
                    print("Discarded duplicate account file")
            except:
                print("Cannot open: "+name)
        print("Found "+str(len(apilist))+" account file(s).")
        writejson()
        #print(apilist)
    except:
        print("Please enter your Twitter App Keys into four seperate lines in a text file in this order: \n 1.consumer key\n 2.consumer secret\n 3.access token\n 4.access token secret\n Place the text file into the input directory and rerun twweet-cli")

#function to pick active account
def pick_acc():

    accselmsg="Please enter a number corresponding to the account you with to use: \n"
    for i in range(0,len(apilist)):
        accdetail=str(i)+" - "+apilist[i]["acc_name"]+"\n"
        accselmsg+=accdetail
    print(accselmsg)
    accselect=int(input())
    print("Setting current account to "+apilist[accselect]["acc_name"])

#function to download the tweets of a particular hashtag
def get_tweets_of_hashtag(hash_tag):
    all_tweets = []
    new_tweets = []
    print("Please be patient while we download the tweets")

    api = get_api(apilist[accselect])
    new_tweets = tweepy.Cursor(api.search, q=hash_tag).items(200)

    while new_tweets:
        for tweet in new_tweets:
            all_tweets.append(tweet.text.encode("utf-8"))
            #max_id will be id of last tweet when loop completes. shitty wasy of doing things
            max_id = tweet.id

        print("We have got {} tweets so far".format(len(all_tweets)))
        new_tweets = tweepy.Cursor(api.search, q=hash_tag).items(200)

        if (len(all_tweets)) >= 1000:
            break

    with open('{}s.csv'.format(hash_tag), 'w') as f:
        writer = csv.writer(f)
        for tweet in all_tweets:
            if tweet:
                writer.writerow([tweet])

    print("1000 tweets have been saved to {}s.csv".format(hash_tag))


def get_trending_topics():

    api = get_api(apilist[accselect])

    trends1 = api.trends_place(1) #1 for worldwide
    data = trends1[0]
    trends = data['trends']
    print("\nTrending topics worldwide :")
    for item in trends:
        print(item['name'])

def process_or_store(tweet):
    print(json.dumps(tweet))

def readTimeLine(api):
    for status in tweepy.Cursor(api.home_timeline).items(10):
        # process a single status
        # print(status.text)
        process_or_store(status._json)

def getFollowersList(api):
    for friend in tweepy.Cursor(api.user_timeline).items(10):
        process_or_store(friend._json)

def getTweets(api):
    for tweet in tweepy.Cursor(api.user_timeline).items(10):
        process_or_store(tweet._json)


def main():

    initaccs()
    pick_acc()
    api = get_api(apilist[accselect])

    option = input('Enter \'twweet\' or \'get\' or \'read\': ')
    if option == 'twweet':
        tweet = input('Enter your twweet\n')
        api.update_status(status=tweet)
        # Yes, tweet is called 'status' rather confusing
    elif option == 'get':
        option = input('1.Get tweets of any user \n2.Get tweets of particular hashtag \n3.Get trending topics\n4.Read your timeline\n5.Get your followers list\n6.Get your tweets\n')
        if option == '1':
            get_all_tweets(input('Enter the username whose tweet\'s you want to grab: '))
        elif option == '2':
            get_tweets_of_hashtag(input('Enter the hashtag: '))
        elif option == '3':
            get_trending_topics()
        elif option == '4':
            readTimeLine(api)
        elif option == '5':
            getFollowersList(api)
        elif option == '6':
            getTweets(api)
    elif option == 'read':
        main()

if __name__ == "__main__":
  main()
