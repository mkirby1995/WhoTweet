"""SQL Alchmey models for WhoTweet"""
#FLASK_APP=WhoTweet:APP flask run

from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()

class Bird(DB.Model):
    """Twitter users that we pull and analyze tweets for"""
    id = DB.Column(DB.BigInteger, primary_key = True)
    name = DB.Column(DB.String(15), nullable = False)
    newest_tweet_id = DB.Column(DB.BigInteger)

    def __repr__(self):
        return '<bird {}>'.format(self.name)

class Tweet(DB.Model):
    """Tweets"""
    id = DB.Column(DB.BigInteger, primary_key = True)
    text = DB.Column(DB.Unicode(300))
    embedding = DB.Column(DB.PickleType, nullable = False)
    bird_id = DB.Column(DB.BigInteger, DB.ForeignKey('bird.id'),
        nullable = False)
    bird = DB.relationship('Bird', backref=DB.backref('tweets', lazy = True))

    def __repr__(self):
        return '<Tweet {}>'.format(self.text)
