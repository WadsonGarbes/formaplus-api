import random
import click
from flask import Blueprint
from faker import Faker
from api.app import db
from api.models import User, Question

fake = Blueprint('fake', __name__)
faker = Faker()


@fake.cli.command()
@click.argument('num', type=int)
def users(num):  # pragma: no cover
    """Cria o número informado de usuários"""
    users = []
    for i in range(num):
        user = User(username=faker.user_name(), email=faker.email(),
                    about_me=faker.sentence())
        db.session.add(user)
        users.append(user)

    db.session.commit()
    print(num, 'users added.')


@fake.cli.command()
@click.argument('num', type=int)
def questions(num):  # pragma: no cover
    """Cria o número informado de questões e associa a usuários aleatórios"""
    users = db.session.scalars(User.select()).all()
    for i in range(num):
        user = random.choice(users)
        question = Question(body=faker.paragraph(), 
                    answer=faker.paragraph(), 
                    author=user,
                    timestamp=faker.date_time_this_year())
        db.session.add(question)
    db.session.commit()
    print(num, 'questions added.')
