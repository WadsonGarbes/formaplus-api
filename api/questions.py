from flask import Blueprint, abort
from apifairy import authenticate, body, response, other_responses

from api import db
from api.models import User, Question
from api.schemas import QuestionSchema
from api.auth import token_auth
from api.decorators import paginated_response
from api.schemas import DateTimePaginationSchema

questions = Blueprint('questions', __name__)
question_schema = QuestionSchema()
questions_schema = QuestionSchema()
update_question_schema = QuestionSchema(partial=True)


@questions.route('/questions', methods=['POST'])
@authenticate(token_auth)
@body(question_schema)
@response(questions_schema, 201)
def new(args):
    """Cria uma nova questão"""
    user = token_auth.current_user()
    question = Question(author=user, **args)
    db.session.add(question)
    db.session.commit()
    return question


@questions.route('/questions/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(question_schema)
@other_responses({404: 'Question not found'})
def get(id):
    """Obtém uma questão por id"""
    return db.session.get(Question, id) or abort(404)


@questions.route('/questions', methods=['GET'])
@authenticate(token_auth)
@paginated_response(questions_schema, order_by=Question.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def all():
    """Obtém todas as questões"""
    return Question.select()


@questions.route('/users/<int:id>/questions', methods=['GET'])
@authenticate(token_auth)
@paginated_response(questions_schema, order_by=Question.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
@other_responses({404: 'Usuário não encontrado'})
def user_all(id):
    """Obtém todas as questões de um usuário específico"""
    user = db.session.get(User, id) or abort(404)
    return user.questions_select()


@questions.route('/questions/<int:id>', methods=['PUT'])
@authenticate(token_auth)
@body(update_question_schema)
@response(question_schema)
@other_responses({403: 'Não é permitida a edição desta pergunta',
                  404: 'Pergunta não encontrada'})
def put(data, id):
    """Edita uma pergunta"""
    question = db.session.get(Question, id) or abort(404)
    if question.author != token_auth.current_user():
        abort(403)
    question.update(data)
    db.session.commit()
    return question


@questions.route('/questions/<int:id>', methods=['DELETE'])
@authenticate(token_auth)
@other_responses({403: 'Proibida a deleção da questão'})
def delete(id):
    """Deleta uma questãot"""
    question = db.session.get(Question, id) or abort(404)
    if question.author != token_auth.current_user():
        abort(403)
    db.session.delete(question)
    db.session.commit()
    return '', 204
