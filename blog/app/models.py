from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from . import db, login_manager
from datetime import datetime, timedelta
from hashlib import md5


class RoomUserAssociation(db.Model):
    __tablename__ = 'rooms_users'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), primary_key=True)
    user = db.relationship("User", cascade="all")
    room = db.relationship("Room", cascade="all")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())


class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    room_users = db.relationship('RoomUserAssociation', cascade="all")

    def is_author(self, user):
        return self.author_id == user.id

    def online_users(self):
        return [room_user for room_user in self.room_users if room_user.user.is_online()]

    def offline_users(self):
        return [room_user for room_user in self.room_users if not room_user.user.is_online()]


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String)
    disabled = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    author_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


class Follow(db.Model):
    __tablename__ = 'follows'
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow())
    follower_id = db.Column(db.Integer(), db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer(), db.ForeignKey('users.id'), primary_key=True)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer(), primary_key=True)
    image_filename = db.Column(db.String(200), default=None)
    title = db.Column(db.String)
    body = db.Column(db.Text())
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow())
    author_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def is_author(self, author):
        return self.author == author


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), unique=True)
    default = db.Column(db.Boolean(), default=False, index=True)
    permissions = db.Column(db.Integer())

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        if self.permissions != 0:
            self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(128), unique=True)
    enabled = db.Column(db.Boolean(), default=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    birthday = db.Column(db.Date())
    phone = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    address = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    news_letter = db.Column(db.Boolean(), default=False)
    salt = db.Column(db.String(128))
    hashed_password = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean(), default=False)
    deleted_at = db.Column(db.DateTime(), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship("Role")
    posts = db.relationship("Post", backref=db.backref('author'), lazy='dynamic')
    following = db.relationship("Follow", foreign_keys=[Follow.follower_id], backref=db.backref('follower', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    followed = db.relationship("Follow", foreign_keys=[Follow.followed_id], backref=db.backref('followed', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship("Comment", backref=db.backref('author'), lazy='dynamic')
    rooms = db.relationship("Room", backref=db.backref('author'), lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    def is_following(self, follower):
        return Follow.query.filter_by(follower_id=follower.id, followed_id=self.id).first() is not None

    def is_followed(self, followed):
        return Follow.query.filter_by(follower_id=self.id, followed_id=followed.id).first() is not None

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        email_hash = md5(self.email.lower().encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=email_hash, size=size, default=default, rating=rating)

    def full_name(self):
        return "{first_name} {last_name}".format(first_name=self.first_name, last_name=self.last_name)

    @property
    def password(self):
        raise AttributeError('Password is not readable attribute')

    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def generate_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def check_token(self, token):
        if User.extract_token(token) != self.id:
            return False

        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()

    def is_online(self):
        return self.last_seen < datetime.utcnow() - timedelta(minutes=2)

    @classmethod
    def extract_token(cls, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf8'))
        except BadData:
            return None
        else:
            return data.get('confirm', None)


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_administrator(self):
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser
