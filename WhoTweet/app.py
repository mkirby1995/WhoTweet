from decouple import config
from flask import Flask, render_template, request
from .models import DB, Bird
from .twitter import add_or_update_bird, add_users
from .predict import predict_user
import os


def create_app():
    """Create and configure an instance of the flask application"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ENV'] = config('ENV')
    DB.init_app(app)

    @app.route('/')
    def root():
        birds = Bird.query.all()
        return render_template('base.html', title = 'Home', birds = birds)

    @app.route('/bird', methods = ['POST'])
    @app.route('/bird/<name>', methods = ['GET'])
    def bird(name = None, message = ''):
        name = name or request.values['bird_name']
        try:
            if request.method == 'POST':
                add_or_update_bird(name)
                message = "Bird {} successfully added!".format(name)
            tweets = Bird.query.filter(Bird.name == name).one().tweets
        except Exception as e:
            message = "Error adding {}: {}".format(name, e)
            tweets = []
        return render_template('user.html', title = name, tweets = tweets,
                               message = message)

    @app.route('/compare', methods=['POST'])
    def compare(message=''):
        user1, user2 = sorted([request.values['user1'],
                               request.values['user2']])
        if user1 == user2:
            message = 'Cannot compare a user to themselves!'
        else:
            prediction = predict_user(user1, user2,
                                      request.values['tweet_text'])
            message = '"{}" is more likely to be said by {} than {}'.format(
                request.values['tweet_text'], user1 if prediction else user2,
                               user2 if prediction else user1)
        return render_template('prediction.html', title='Prediction', message=message)

    @app.route('/reset')
    def reset():
        TWITTER_USERS = ['robert_zubrin', 'JoeBiden', 'ewarren',
                         'realDonaldTrump', 'BetoORouke']
        #CACHE.flushall()
        #CACHED_COMPARISONS.clear()
        DB.drop_all()
        DB.create_all()
        add_users(users = TWITTER_USERS)
        return render_template('base.html', title='Reset database!')

    return app
