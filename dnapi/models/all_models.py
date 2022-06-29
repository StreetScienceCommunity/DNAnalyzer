from utils import db, ma
from flask_login import UserMixin
from marshmallow_sqlalchemy import auto_field
from marshmallow_sqlalchemy.fields import Nested

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    level = db.relationship('Chapter', backref=db.backref('level', lazy=True))

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_score = db.Column(db.Integer, nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)

class ChapterSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Chapter
    id = auto_field()
    level_id = auto_field()

chapter_schema = ChapterSchema()
chapters_schema = ChapterSchema(many=True)

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.String())
    type = db.Column(db.String(), nullable=False)
    hint = db.Column(db.String())
    explanation = db.Column(db.String())
    image_url = db.Column(db.String())
    point = db.Column(db.Integer, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    chapter = db.relationship('Chapter', backref=db.backref('questions', lazy=True))
    choices = db.relationship('Choice', backref=db.backref('Question', lazy=True))

class QuestionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Question
    id = auto_field()
    title = auto_field()
    description = auto_field()
    type = auto_field()
    hint = auto_field()
    image_url = auto_field()
    point = auto_field()
    choices = Nested(ChoiceSchema, many=True)

question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('answers', lazy=True))
    choice_id = db.Column(db.Integer, db.ForeignKey('choice.id'), nullable=False)
    choice = db.relationship('Choice', backref=db.backref('answers', lazy=True))

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('scores', lazy=True))
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    chapter = db.relationship('Chapter', backref=db.backref('scores', lazy=True))