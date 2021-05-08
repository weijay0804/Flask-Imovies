from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app, url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import login_manager
import json


#建立User與Movie的中間表(電影清單)
user_movie = db.Table('user_movie',
                        db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                        db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'))
                    )

#建立User與Movie的中間表(已觀看電影清單)
user_watched_movie = db.Table('user_watched_movie',
                        db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                        db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'))
                    )

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(64), unique = True, index = True)
    original_title = db.Column(db.String(128))
    movie_type = db.Column(db.String(64))
    movie_time = db.Column(db.String(64))
    year = db.Column(db.String(64))
    rate = db.Column(db.Float)
    movie_link = db.Column(db.String(200))
    img_link = db.Column(db.String(200))
    source = db.Column(db.String(64))
    write_in_time = db.Column(db.DateTime(), default = datetime.utcnow)

    @staticmethod
    def write_in_data_hot():
        datas = []
        with open('hot_movies.txt', 'r', encoding='utf-8') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                dic = json.loads(line)
                datas.append(dic)

        for data in datas:
            try:
                movie = Movie.query.filter_by(title = data['title']).first()
                movie.write_in_time = datetime.utcnow()
                db.session.commit()
            except:
                movie = Movie(title = data['title'], original_title = data['ogtitle'], 
                                movie_type = data['movie_type'], movie_time = data['movie_time'], year = data['year'],
                                rate = data['rate'], movie_link = data['link'], img_link = data['img'],
                                source = 'hot_movie')
                db.session.add(movie)
        db.session.commit()

    @staticmethod
    def write_in_data_top():
        datas = []
        with open('top250.txt', 'r', encoding='utf-8') as f:
            while True:
                lines = f.readline()
                if not lines:
                    break
                dic = json.loads(lines)
                datas.append(dic)

        for data in datas:
            movie = Movie.query.filter_by(title = data['title']).first()
            if movie is None:
                movie = Movie(title = data['title'], original_title = data['ogtitle'], 
                            movie_type = data['movie_type'], movie_time = data['movie_time'], year = data['year'],
                            rate = data['rate'], movie_link = data['link'], img_link = data['img'],
                            source = 'top_movie')
                db.session.add(movie)
            elif movie.source == 'top_movie':
                movie.write_in_time = datetime.utcnow()
                db.session.add(movie)
            else:
                movie.source = 'hot_top_movie'
                db.session.add(movie)
                
        db.session.commit()

    
    def __repr__(self):
        return '<Movie: %r>' % self.title

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    email = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(128))
    confiremd = db.Column(db.Boolean, default = False)
    movies = db.relationship('Movie', secondary = user_movie, 
                                    backref = db.backref('users', lazy = 'dynamic'),
                                    lazy = 'dynamic')
    watched_movies = db.relationship('Movie', secondary = user_watched_movie, 
                                    backref = db.backref('watched_users', lazy = 'dynamic'),
                                    lazy = 'dynamic')


    '''使用者密碼處理區域開始'''

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    '''使用者密碼處理區域結束'''


    '''使用者權杖設定區域開始'''

    def gengerate_confirmation_token(self, expiration = 3600):
        '''產生認證權杖，到期時間為3600s'''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        '''確認權杖'''
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        if data.get('confirm') != self.id:
            return False

        self.confiremd = True
        db.session.add(self)
        return True

    '''重新設定密碼區域開始'''

    def generate_reset_passsword_token(self, expiration=3600):
        '''產生重設密碼的權杖'''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset' : self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        '''重設密碼函式'''
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        user = User.query.get(data.get('reset'))

        if user is None:
            return False

        user.password = new_password
        db.session.add(user)
        return True

    '''重新設定密碼區域結束'''


    '''重新設定email區域開始'''

    def generate_change_email_token(self, new_email, expiration = 3600):
        '''產生變更email的權杖'''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email' : self.id, 'new_email' : new_email}).decode('utf-8')

    def change_email(self, token):
        '''變更email函式'''
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        if data.get('change_email') != self.id:
            return False

        new_email = data.get('new_email')
        if new_email is None:
            return False

        if self.query.filter_by(email = new_email).first() is not None: #確認email不重複
            return False

        self.email = new_email
        db.session.add(self)
        return True

    '''重新設定email區域結束'''


    '''使用者權杖設定區域結束'''


    def __repr__(self):
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(user_id):
    '''載入使用者的涵式'''
    return User.query.get(int(user_id))





