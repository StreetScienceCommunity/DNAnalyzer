from flask import Blueprint, flash, g, redirect, request, session, url_for, jsonify, send_file, make_response, \
    render_template
from models.all_models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

bp = Blueprint('dnapi', __name__, url_prefix='/')


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
    return render_template("games/chapter.html", questions=questions, q_len=len(questions), chapter=chapter,
                           chapters=chapters)


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
    chapters = Chapter.query.all()
    chapters = chapters_schema.dump(chapters)

    # check choice submitted if right wrong or miss
    cur_score = 0
    for question in questions_dump:
        submitted_answers = set(form.getlist(question['id']))
        # for aws_id in submitted_answers:
        #     new_answer = Answer(
        #         user_id=current_user.id,
        #         choice_id=aws_id
        #     )
        #     db.session.add(new_answer)
        #     db.session.commit()
        selected_correct = 0
        missed_wrong = 0
        if not form.get(question['id']):
            question['missed'] = True
        for choice in question['choices']:
            if choice['correctness']:
                if choice['id'] in submitted_answers:
                    choice['state'] = 'correct'
                    selected_correct += 1
                else:
                    choice['state'] = 'missed'
            else:
                if choice['id'] in submitted_answers:
                    choice['state'] = 'wrong'
                else:
                    missed_wrong += 1
        if question['type'] in ['choose_one', 'grid']:
            if selected_correct > 0:
                question['score'] = question['point']
                cur_score += question['point']
            else:
                question['score'] = 0
        else:
            correct_sum = selected_correct + missed_wrong
            question['score'] = question['point'] * 0 if correct_sum == 0 else len(question['choices']) / correct_sum
    return render_template("games/quiz_result.html", questions=questions_dump, q_len=len(questions),
                           chapter=chapter_dump, score=cur_score, chapters=chapters)
