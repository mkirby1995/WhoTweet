""" Retrives tweets, embedings and persist in the database """

import tweepy
import basilica
from decouple import config
from .models import DB, Tweet, User

TWITTER_AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),
                                   config('TWITTER_CONSUMER_SECRET'))

TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),
                              config('TWITTER_ACCESS_TOKEN_SECRET'))

TWITTER = tweepy.API(TWITTER_AUTH)

BASILICA = basilica.Connection(config('BASILICA_KEY'))

users = ['gvanrossum', 'NYTScience']

def add_or_update_user(username):
    """
    Add or update a user and their tweets
    """
    try:
        twitter_user = TWITTER.get_user(username)
        db_user = (User.query.get(twitter_user.id) or
                   User(id=twitter_user.id, name=username))

        DB.session.add(db_user)

        tweets = twitter_user.timeline(
            count=250, exclude_replies = True, include_rts = False,
            tweet_mode = 'extended', since_id = db.user.newest_tweet_id)
        if tweets:
            db_user.newest_tweet_id = tweet[0].id

        for tweet in tweets:
            embedding = BASILICA.embed_sentence(tweet.full_text,
                                                model = 'twitter')
            db_tweet = Tweet(id = tweet.id, text = tweet.full_text[:300],
                             embedding = embedding)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print("Error processing {}: {}".format(username, e))
        raise e
    else:
        DB.session.commit()
