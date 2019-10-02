from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post, Comment, Permission, Role


def _load_roles():
    roles = [
        {'name': 'User', 'permissions': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE], 'default': True},
        {'name': 'Moderator',
         'permissions': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
         'default': False},
        {'name': 'Administrator',
         'permissions': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE,
                         Permission.ADMIN], 'default': False}
    ]

    for role_param in roles:
        role = Role.query.filter_by(name=role_param['name']).first()
        permissions = role_param.pop('permissions')
        if role is None:
            role = Role(**role_param)

        role.reset_permission()

        for perm in permissions:
            role.add_permission(perm)

        db.session.add(role)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def _load_admin(count=1):
    fake = Faker()
    for _ in range(count):
        user = User(email=fake.email(), username=fake.user_name(), confirmed=True, first_name=fake.first_name(),
                    last_name=fake.last_name(), about_me=fake.text(), phone=fake.phone_number(),
                    birthday=fake.past_date(), address=fake.address(), password='123456', role=Role.query.filter_by(name='Administrator').first())
        db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def _load_users(count=100):
    fake = Faker()
    for _ in range(count):
        user = User(email=fake.email(), username=fake.user_name(), confirmed=True, first_name=fake.first_name(),
                    last_name=fake.last_name(), about_me=fake.text(), phone=fake.phone_number(),
                    birthday=fake.past_date(), address=fake.address(), password='123456')
        db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def _load_posts_comments(count=100):
    fake = Faker()
    user_count = User.query.count()
    for _ in range(count):
        user = User.query.offset(randint(0, user_count - 1)).first()
        post = Post(image_filename=None, title=fake.sentence(), body=fake.text(), timestamp=fake.past_date(),
                    author=user)
        db.session.add(post)
        for _ in range(4):
            comment = Comment(author=User.query.offset(randint(0, user_count - 1)).first(), post=post, body=fake.text())
            db.session.add(comment)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def exec_fixtures():
    _load_roles()
    _load_admin()
    _load_users()
    _load_posts_comments()
