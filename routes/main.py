import collections
import json
import os
from pathlib import Path

from flask import Blueprint, flash, g, redirect, request, session, url_for, jsonify, send_file, make_response, \
    render_template
from models.all_models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

bp = Blueprint('dnapi', __name__, url_prefix='/')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Function to log in the user
    @return: index page if login is successfully else return to login page with message
    @rtype: flask template
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('index'))
        else:
            flash('Wrong username or password', category='warning')
    return render_template("login.html")


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Function to register the user
    @return: return to the register page with success or error message
    @rtype: flask template
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')
        user = Users.query.filter_by(username=username).first()
        if user:
            flash('username already exists', category='warning')
        elif len(username) < 3 or len(username) > 20:
            flash('username must be of length 3-20 characters', category='warning')
        elif len(password) < 3 or len(password) > 20:
            flash('password must be of length 3-20 characters', category='warning')
        elif password != repeat_password:
            flash('Passwords are not identical', category='warning')
        else:
            new_user = Users(username=username, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created', category='success')
            return redirect(url_for('dnapi.login'))
    # if request.method == 'GET':
    return render_template("register.html")


@bp.route('/logout')
@login_required
def logout():
    """
    Log out the user
    @return: return to the login page
    @rtype: flask template redirect
    """
    logout_user()
    flash('Logged out successfully', category='success')
    return redirect(url_for('dnapi.login'))


@bp.route('/level/<level_id>/intro')
def intro(level_id):
    """
    Function for accessing each level's introduction page
    @param level_id: id of level
    @type level_id: integer in string form
    @return: return the certain introduction page
    @rtype: flask template
    """
    return render_template("games/level%s/intro.html" % level_id, cur_lvl_intro=int(level_id))


@bp.route('/level/<level_id>/chapter/<chapter_id>')
@login_required
def chapter(level_id, chapter_id):
    """
    view function for quiz page
    @param level_id: the level id for showing related quiz questions
    @type level_id: integer
    @param chapter_id: the chapter id for showing related quiz questions
    @type chapter_id: integer
    @return: flask template for quiz
    @rtype: flask template
    """
    cur_chapter_raw = db.engine.execute(
        'select * from chapter where level_id = %s and order_id = %s' % (level_id, chapter_id))
    cur_chapter = [dict(row) for row in cur_chapter_raw]
    chapter_dump, questions_dump = quiz_questions_helper(cur_chapter[0]['id'])
    return render_template("games/chapter.html", questions=questions_dump, chapter=chapter_dump)


@bp.route('/quiz/<chapter_id>/submit', methods=['POST'])
@login_required
def quiz_submit(chapter_id):
    """
    function for receiving quiz answers, checking them, store the score and return to the result page
    @param chapter_id: the chapter id for showing related quiz questions
    @type chapter_id: integer
    @return: return the quiz result page
    @rtype: flask template
    """
    form = request.form
    chapter_dump, questions_dump = quiz_questions_helper(chapter_id)
    # check choice submitted if right wrong or miss
    cur_score = 0
    db.engine.execute(
        "delete from answer where answer.choice_id in  ( select answer.choice_id from answer, choice, chapter, users, question where answer.choice_id = choice.id and choice.question_id = question.id and question.chapter_id = chapter.id and chapter.id = %s and users.id = %s )" % (
            chapter_id, current_user.id))
    db.engine.execute("delete from score where chapter_id = %s and user_id=%s" % (chapter_id, current_user.id))

    # check score for each question
    i = 0
    while i < len(questions_dump):
        j = i

        # update answer to the database for each choice selected
        submitted_answers = set(form.getlist(questions_dump[i]['id']))
        for aws_id in submitted_answers:
            new_answer = Answer(
                user_id=current_user.id,
                choice_id=aws_id
            )
            db.session.add(new_answer)
            db.session.commit()

        # start counting selected correct choices and wrong choices that user didn't select
        selected_correct = 0
        missed_wrong = 0
        if questions_dump[i]['type'] in ['choose_one', 'grid']:
            if not form.get(questions_dump[i]['id']):
                questions_dump[i]['missed'] = True
            for choice in questions_dump[i]['choices']:
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
            if selected_correct > 0:
                questions_dump[i]['score'] = questions_dump[i]['point']
                cur_score += questions_dump[i]['point']
            else:
                questions_dump[i]['score'] = 0
        else:
            total_choice_num = 0
            while j < len(questions_dump):
                if questions_dump[j]['title'] != questions_dump[i]['title']:
                    break
                if not form.get(questions_dump[j]['id']):
                    questions_dump[j]['missed'] = True
                for choice in questions_dump[j]['choices']:
                    total_choice_num += 1
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
                j += 1
            correct_sum = selected_correct + missed_wrong
            question_score = 0
            if correct_sum == 0:
                question_score = 0
            else:
                question_score = round(correct_sum / total_choice_num * questions_dump[i]['point'])
            cur_score += question_score
            for k in range(i, j):
                questions_dump[k]['score'] = question_score
            i = j - 1
        i += 1

    # update final score to the database
    new_score = Score(
        score=cur_score,
        user_id=current_user.id,
        chapter_id=chapter_id
    )
    db.session.add(new_score)
    db.session.commit()

    ranking = get_ranking(chapter_id)
    return render_template("games/quiz_result.html", questions=questions_dump,
                           chapter=chapter_dump, score=cur_score, ranking=ranking)


def left_chapter_menu_helper():
    """
    helper function to return a lvl->chapter dictionary for the chapter menu
    @return: a lvl->chapter dictionary
    @rtype: dictionary
    """
    levels = Level.query.all()
    levels = levels_schema.dump(levels)
    level_dict = {}
    for lvl in levels:
        if lvl['chapters']:
            level_dict[lvl['id']] = []
            for ch in lvl['chapters']:
                chapter = Chapter.query.get(ch)
                chapter = chapter_schema.dump(chapter)
                level_dict[lvl['id']].append(chapter)

    if current_user.is_authenticated:
        done_chapters = db.engine.execute('select chapter_id from score where user_id = %s' % (current_user.id))
        done_chapters_list = [row[0] for row in done_chapters]
        if done_chapters_list:
            for chapters in level_dict.values():
                for ch in chapters:
                    if ch['id'] in done_chapters_list:
                        ch['done'] = 1
    return level_dict


def quiz_questions_helper(chapter_id):
    """
    function to get a chapter object and a list of questions of the particular chapter by chapter id
    @param chapter_id: id of the chapter
    @type chapter_id: integer
    @return: a chapter object and a list of questions of the particular chapter
    @rtype: chapter object and list
    """
    questions = Question.query.filter_by(chapter_id=chapter_id).order_by(Question.id).all()
    questions_dump = questionswithanswers_schema.dump(questions)
    cur_chapter = Chapter.query.get(chapter_id)
    chapter_dump = chapter_schema.dump(cur_chapter)
    return chapter_dump, questions_dump


def handle_addtime(result_raw):
    """
    make raw sql result to list of dictionaries and remove microseconds from addtime field
    @param result_raw: raw sql result
    @type result_raw: raw sql result
    @return: sql result in the form of a list of dictionary
    @rtype: a list of dictionary
    """
    result = [dict(row) for row in result_raw]
    for c in result:
        if c['add_time']:
            c['add_time'] = c['add_time'].replace(microsecond=0)
    return result


@bp.route('/progress')
@login_required
def progress():
    """
    view function for progress page
    @return: return the progress page
    @rtype: flask template
    """
    # get raw query result
    chapters_raw = db.engine.execute(
        'select chapter.id, order_id, name, score, add_time, level_id from chapter left join score on score.chapter_id = chapter.id and score.user_id = %s and chapter.level_id = %s order by chapter.id' % (
            current_user.id, 1))

    # process time format and make the result a dictionary
    chapters_processed = handle_addtime(chapters_raw)

    # convert it into a lvl_id:[chapters] dictionary
    chapter_lvl_dict = {}
    for c in chapters_processed:
        if c['level_id'] not in chapter_lvl_dict:
            chapter_lvl_dict[c['level_id']] = []
        chapter_lvl_dict[c['level_id']].append(c)

    # sort it by the lvl id
    sorted_dict = collections.OrderedDict(sorted(chapter_lvl_dict.items()))

    return render_template("progress.html", lvl_dict=sorted_dict)


def get_ranking(chapter_id):
    """
    function to return top 5 result for certain chapter
    @param chapter_id: id of the chapter
    @type chapter_id: integer
    @return: a list of ranking
    @rtype: list
    """
    ranking_raw = db.engine.execute(
        'select username, score, add_time, user_id from score, users where score.user_id = users.id and score.chapter_id = %s order by score DESC, add_time ASC limit 5' % (
            chapter_id))
    ranking = handle_addtime(ranking_raw)
    return ranking


@bp.route('/level/<level_id>/chapter/<chapter_id>/result')
@login_required
def chapter_result(level_id, chapter_id):
    """
    function for receiving quiz answers
    @param level_id: the level id of the chapter
    @type level_id: integer
    @param chapter_id: the chapter id for showing related quiz result
    @type chapter_id: integer
    @return: return result page
    @rtype: flask template
    """
    cur_chapter_raw = db.engine.execute(
        'select * from chapter where level_id = %s and order_id = %s' % (level_id, chapter_id))
    cur_chapter = [dict(row) for row in cur_chapter_raw]
    chapter_dump, questions_dump = quiz_questions_helper(cur_chapter[0]['id'])
    selected_choices_raw = db.engine.execute(
        "select question.id as q_id,  choice.id as c_id from answer, chapter, choice, question where choice.question_id = question.id and question.chapter_id = chapter.id and choice.id = answer.choice_id and user_id = %s and chapter.id = %s order by question.id, choice.id" % (
            current_user.id, cur_chapter[0]['id']))
    ranking = get_ranking(cur_chapter[0]['id'])

    selected_choices = {}
    for row in selected_choices_raw:
        if str(row[0]) not in selected_choices:
            selected_choices[str(row[0])] = []
        selected_choices[str(row[0])].append(str(row[1]))

    score = Score.query.filter_by(user_id=current_user.id, chapter_id=cur_chapter[0]['id']).first()

    for question in questions_dump:
        if question['id'] not in selected_choices:
            question['missed'] = True
        for choice in question['choices']:
            if choice['correctness']:
                if question['id'] in selected_choices and choice['id'] in selected_choices[question['id']]:
                    choice['state'] = 'correct'
                else:
                    choice['state'] = 'missed'
            else:
                if question['id'] in selected_choices and choice['id'] in selected_choices[question['id']]:
                    choice['state'] = 'wrong'
    return render_template("games/quiz_result.html", questions=questions_dump, cur_lvl=level_id,
                           chapter=chapter_dump, score=score.score, ranking=ranking)


@bp.route('/galaxy_history')
@login_required
def galaxy_history():
    """
    view function for galaxy history result
    @return: return galaxy history result page
    @rtype: flask template
    """
    SITE_ROOT = Path(__file__).parent.parent
    filename = os.path.join(SITE_ROOT, 'game', 'dummy_result.json')
    with open(filename) as test_file:
        json_result = json.load(test_file)
    chapter = Chapter.query.get(8)

    # calculate score
    num_step = 0  # total number of steps
    score = 0  # user score
    for step_num, step_res in json_result['steps'].items():
        num_step += 1
        # check if using the same tool
        if step_res['tool_id'] and step_res['tool_id']['status']:
            score += 5
            # if using the same tool, then check tool version
            if step_res['tool_version'] and step_res['tool_version']['status']:
                score += 1
            # if using the same tool, then check parameters
            if step_res['parameters'] and step_res['parameters']['number_of_mismatches'] and step_res['parameters'][
                'total_number_of_param']:
                score += (step_res['parameters']['number_of_mismatches'] / step_res['parameters'][
                    'total_number_of_param']) * 2
    normalized_score = round(score / (num_step * 8) * 100, 2)
    return render_template("games/level2/galaxy_result.html", result=json_result, chapter=chapter,
                           score=normalized_score)


@bp.context_processor
def provide_menu():
    """
    function to provide global variable for all the templates to use
    @return: a dictionary for level->[chapters]
    @rtype: dictionary
    """
    level_dict = left_chapter_menu_helper()
    return {'level_dict': level_dict}
