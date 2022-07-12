from flask import Blueprint, flash, g, redirect, request, session, url_for, jsonify, send_file, make_response, render_template
import io
import base64
from PIL import Image
from models.all_models import *
from werkzeug.security  import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
bp = Blueprint('dnapi', __name__, url_prefix='/')


@bp.route('/hello', methods=['GET'])
def hello():
    return jsonify({"msg": "hello!"})


@bp.route('/img', methods=['GET'])
def access_img(img_path):
    img = get_encoded_img(img_path)
    # prepare the response: data
    response_data = {"key1": 2, "key2": 3, "image": img}
    return jsonify(response_data)


@bp.route('/questions', methods=['GET'])
@login_required
def get_questions():
    all_questions = Question.query.filter_by(chapter_id='1').order_by(Question.id).all()
    # for q in all_questions:
    #     if q.image_url:
    #         q.image_url = get_encoded_img(q.image_url)
    # return '123'
    return jsonify(questions_schema.dump(all_questions))


@bp.route('/chapter/<id>', methods=['GET'])
def get_questions_by_chapter(id):
    questions = Question.query.filter_by(chapter_id=id).order_by(Question.id).all()
    # for q in all_questions:
    #     if q.image_url:
    #         q.image_url = get_encoded_img(q.image_url)
    # return '123'
    return jsonify(questions_schema.dump(questions))


def get_encoded_img(image_path):
    full_path = "./images/" + image_path
    img = Image.open(full_path, mode='r')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    my_encoded_img = base64.encodebytes(img_byte_arr.getvalue()).decode('ascii')
    return my_encoded_img


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('index'))
        else:
            flash('Wrong username or password', category='warning')
    return render_template("login.html")


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')
        user = User.query.filter_by(username=username).first()
        if user:
            flash('username already exists', category='warning')
        elif len(username) < 3 or len(username) > 20:
            flash('username must be of length 3-20 characters', category='warning')
        elif len(password) < 3 or len(password) > 20:
            flash('password must be of length 3-20 characters', category='warning')
        elif password != repeat_password:
            flash('Passwords are not identical', category='warning')
        else:
            new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created', category='success')
            return redirect(url_for('dnapi.login'))
    # if request.method == 'GET':
    return render_template("register.html")


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', category='success')
    return redirect(url_for('dnapi.login'))


@bp.route('/level1/intro')
def intro():
    chapters = Chapter.query.all()
    chapters = chapters_schema.dump(chapters)
    return render_template("games/intro.html", chapters=chapters)


@bp.route('/level1/chapter/<chapter_id>')
@login_required
def chapter(chapter_id):
    """
    view function for quiz page
    @param chapter_id: the chapter id for showing related quiz questions
    @return: the template for quiz
    """
    questions = Question.query.filter_by(chapter_id=chapter_id).order_by(Question.id).all()
    questions = questions_schema.dump(questions)
    chapter = Chapter.query.get(chapter_id)
    chapter = chapter_schema.dump(chapter)
    chapters = Chapter.query.all()
    chapters = chapters_schema.dump(chapters)
    return render_template("games/chapter.html",  questions=questions, q_len= len(questions), chapter=chapter, chapters=chapters)


@bp.route('/quiz/<chapter_id>/submit', methods=['POST'])
@login_required
def quiz_submit(chapter_id):
    """
    function for receiving quiz answers
    @param chapter_id: the chapter id for showing related quiz questions
    @return: show result
    """

    form = request.form
    questions = Question.query.filter_by(chapter_id=chapter_id).order_by(Question.id).all()
    questions_dump = questionswithanswers_schema.dump(questions)
    chapter = Chapter.query.get(chapter_id)
    chapter_dump = chapter_schema.dump(chapter)

    # check choice submitted if right wrong or miss
    for question in questions_dump:
        if not form.get(question['id']):
            question['missed'] = True
        anwsers = set(form.getlist(question['id']))
        for choice in question['choices']:
            if choice['correctness']:
                if choice['id'] in anwsers:
                    choice['state'] = 'correct'
                else:
                    choice['state'] = 'missed'
            else:
                if choice['id'] in anwsers:
                    choice['state'] = 'wrong'

    return render_template("games/quiz_result.html", questions=questions_dump, q_len= len(questions), chapter=chapter_dump)