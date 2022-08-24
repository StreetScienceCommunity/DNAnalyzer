from utils import db, ma
from flask_login import UserMixin
from marshmallow import fields
from marshmallow_sqlalchemy import auto_field
from marshmallow_sqlalchemy.fields import Nested
from datetime import datetime


class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)


class Choice(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    content = db.Column(db.String(), nullable=False)
    correctness = db.Column(db.Boolean(), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)


class ChoiceSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Choice

    id = auto_field()
    content = auto_field()


choice_schema = ChoiceSchema()
choices_schema = ChoiceSchema(many=True)


class ChoicewithanwersSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Choice

    id = fields.String()
    content = auto_field()
    correctness = auto_field()


choicewithanswers_schema = ChoicewithanwersSchema()
choiceswithanswers_schema = ChoicewithanwersSchema(many=True)


class Question(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.String())
    type = db.Column(db.String(), nullable=False)
    hint = db.Column(db.String())
    explanation = db.Column(db.String())
    image_name = db.Column(db.String())
    point = db.Column(db.Integer, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    choices = db.relationship('Choice', backref='question', order_by=Choice.id)


class QuestionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Question

    id = auto_field()
    title = auto_field()
    description = auto_field()
    type = auto_field()
    hint = auto_field()
    image_name = auto_field()
    point = auto_field()
    explanation = auto_field()
    choices = Nested(ChoiceSchema, many=True)


question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)


class QuestionwithanswersSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Question

    id = fields.String()
    title = auto_field()
    description = auto_field()
    type = auto_field()
    hint = auto_field()
    image_name = auto_field()
    point = auto_field()
    explanation = auto_field()
    chapter_id = auto_field()
    choices = Nested(ChoicewithanwersSchema, many=True)


questionwithanswers_schema = QuestionwithanswersSchema()
questionswithanswers_schema = QuestionwithanswersSchema(many=True)


class Chapter(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    total_score = db.Column(db.Integer, nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    url = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    questions = db.relationship('Question', backref='chapter', order_by=Question.id)


class ChapterSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Chapter

    id = auto_field()
    level_id = auto_field()
    url = auto_field()
    name = auto_field()
    total_score = auto_field()
    order_id = auto_field()


chapter_schema = ChapterSchema()
chapters_schema = ChapterSchema(many=True)


class Level(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    chapters = db.relationship('Chapter', backref=db.backref('level', lazy=True))


class LevelSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Level

    id = auto_field()
    name = auto_field()
    chapters = auto_field()


level_schema = LevelSchema()
levels_schema = LevelSchema(many=True)


class Answer(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('Users', backref=db.backref('answers', lazy=True))
    choice_id = db.Column(db.Integer, nullable=False)
    __table_args__ = (
        # this can be db.PrimaryKeyConstraint if you want it to be a primary key
        db.UniqueConstraint('user_id', 'choice_id'),
    )


class Score(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('Users', backref=db.backref('scores', lazy=True))
    chapter_id = db.Column(db.BigInteger, nullable=False)
    add_time = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)