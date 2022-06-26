from utils import db, ma
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_score = db.Column(db.Integer, nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    level = db.relationship('Level', backref=db.backref('chapters', lazy=True))


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
    # choices = db.relationship('Choice', backref=db.backref('Question', lazy=True))

class QuestionSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("id", "title", "description", "type", "hint", "image_url", "point")

question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)

class Choice(db.Model):
    id: int
    content: str
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(), nullable=False)
    correctness = db.Column(db.Boolean(), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    question = db.relationship('Question', backref=db.backref('choices', lazy=True))

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