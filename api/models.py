from datetime import datetime, timedelta
from hashlib import md5
import secrets
from time import time

from flask import current_app, url_for
import jwt
import sqlalchemy as sqla
from sqlalchemy import orm as sqla_orm
from werkzeug.security import generate_password_hash, check_password_hash

from api.app import db


class Updateable:
    def update(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)


class Token(db.Model):
    __tablename__ = 'tokens'

    id = sqla.Column(sqla.Integer, primary_key=True)
    access_token = sqla.Column(sqla.String(64), nullable=False, index=True)
    access_expiration = sqla.Column(sqla.DateTime, nullable=False)
    refresh_token = sqla.Column(sqla.String(64), nullable=False, index=True)
    refresh_expiration = sqla.Column(sqla.DateTime, nullable=False)
    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey('users.id'),
                          index=True)

    user = sqla_orm.relationship('User', back_populates='tokens')

    def generate(self):
        self.access_token = secrets.token_urlsafe()
        self.access_expiration = datetime.utcnow() + \
            timedelta(minutes=current_app.config['ACCESS_TOKEN_MINUTES'])
        self.refresh_token = secrets.token_urlsafe()
        self.refresh_expiration = datetime.utcnow() + \
            timedelta(days=current_app.config['REFRESH_TOKEN_DAYS'])

    def expire(self):
        self.access_expiration = datetime.utcnow()
        self.refresh_expiration = datetime.utcnow()

    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        db.session.execute(Token.delete().where(
            Token.refresh_expiration < yesterday))


class User(Updateable, db.Model):
    __tablename__ = 'users'

    id = sqla.Column(sqla.Integer, primary_key=True)
    username = sqla.Column(sqla.String(64), index=True, unique=True,
                           nullable=False)
    email = sqla.Column(sqla.String(120), index=True, unique=True,
                        nullable=False)
    password_hash = sqla.Column(sqla.String(128))
    about_me = sqla.Column(sqla.String(140))
    first_seen = sqla.Column(sqla.DateTime, default=datetime.utcnow)
    last_seen = sqla.Column(sqla.DateTime, default=datetime.utcnow)

    tokens = sqla_orm.relationship('Token', back_populates='user',
                                   lazy='noload')
    questions = sqla_orm.relationship('Question', back_populates='author',
                                  lazy='noload')

    def questions_select(self):
        return Question.select().where(sqla_orm.with_parent(self, User.questions))


    def __repr__(self):  # pragma: no cover
        return '<User {}>'.format(self.username)

    @property
    def url(self):
        return url_for('users.get', id=self.id)

    @property
    def avatar_url(self):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon'

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.utcnow()

    def generate_auth_token(self):
        token = Token(user=self)
        token.generate()
        return token

    @staticmethod
    def verify_access_token(access_token, refresh_token=None):
        token = db.session.scalar(Token.select().filter_by(
            access_token=access_token))
        if token:
            if token.access_expiration > datetime.utcnow():
                token.user.ping()
                db.session.commit()
                return token.user

    @staticmethod
    def verify_refresh_token(refresh_token, access_token):
        token = db.session.scalar(Token.select().filter_by(
            refresh_token=refresh_token, access_token=access_token))
        if token:
            if token.refresh_expiration > datetime.utcnow():
                return token

            # someone tried to refresh with an expired token
            # revoke all tokens from this user as a precaution
            token.user.revoke_all()
            db.session.commit()

    def revoke_all(self):
        db.session.execute(Token.delete().where(Token.user == self))

    def generate_reset_token(self):
        return jwt.encode(
            {
                'exp': time() + current_app.config['RESET_TOKEN_MINUTES'] * 60,
                'reset_email': self.email,
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_token(reset_token):
        try:
            data = jwt.decode(reset_token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except jwt.PyJWTError:
            return
        return db.session.scalar(User.select().filter_by(
            email=data['reset_email']))


class Question(Updateable, db.Model):
    __tablename__ = 'questions'

    id = sqla.Column(sqla.Integer, primary_key=True)
    body = sqla.Column(sqla.String(1024))
    answer = sqla.Column(sqla.String(512))
    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey(User.id), index=True)

    author = sqla_orm.relationship('User', back_populates='questions')

    def __repr__(self):  # pragma: no cover
        return '<Question {}>'.format(self.text)

    @property
    def url(self):
        return url_for('questions.get', id=self.id)
