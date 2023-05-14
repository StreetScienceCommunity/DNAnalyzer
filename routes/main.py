import collections
import json
import os
from pathlib import Path

from flask import Blueprint, flash, redirect, request, url_for, render_template
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

    if level_id == "3" and chapter_id == "4":
        if current_user.is_authenticated:
            return redirect(url_for('dnapi.paper_writing', ifFinished=False))
        else:
            return redirect(url_for('dnapi.login'))

    cur_chapter_raw = db.engine.execute(
        'select * from chapter where level_id = %s and order_id = %s' % (level_id, chapter_id))
    cur_chapter = [dict(row) for row in cur_chapter_raw]

    chapter_dump, questions_dump = quiz_questions_helper(cur_chapter[0]['id'])
    return render_template("games/chapter.html", questions=questions_dump, chapter=chapter_dump)


def delete_previous_result(chapter_id):
    """
        function deleting previous results with given chapter_id and logged_in user
        @param chapter_id: the chapter id for showing related quiz questions
        @type chapter_id: integer
        @return: return the quiz result page
        @rtype: flask template
    """
    if current_user.is_authenticated:
        db.engine.execute(
            "delete from answer where answer.choice_id in  ( select answer.choice_id from answer, choice, chapter, users, question where answer.choice_id = choice.id and choice.question_id = question.id and question.chapter_id = chapter.id and chapter.id = %s and users.id = %s )" % (
                chapter_id, current_user.id))
        db.engine.execute(
            "delete from open_answer where open_answer.id in  ( select open_answer.id from open_answer, question where open_answer.question_id = question.id and question.chapter_id = %s and open_answer.user_id = %s )" % (
                chapter_id, current_user.id))
        db.engine.execute("delete from score where chapter_id = %s and user_id=%s" % (chapter_id, current_user.id))


def store_quiz_results(chapter_id, form):
    """
        function for storing quiz results
        @param chapter_id: the chapter id for showing related quiz questions
        @type chapter_id: integer
        @param form: user submitted form
        @type form: dict
        @return: return the quiz result page
        @rtype: flask template
    """
    chapter_dump, questions_dump = quiz_questions_helper(chapter_id)
    cur_score = 0

    # delete old results if the user is authenticated
    delete_previous_result(chapter_id)

    # check score for each question
    i = 0
    while i < len(questions_dump):
        j = i
        if questions_dump[i]['type'] in ['choose_one', 'grid', 'choose_many', 'grid_checkbox']:
            submitted_answers = set(form.getlist(questions_dump[i]['id']))
            # if the user is_authenticated, update answer to the database for each choice selected
            if current_user.is_authenticated:
                for aws_id in submitted_answers:
                    new_answer = Answer(
                        user_id=current_user.id,
                        choice_id=aws_id
                    )
                    db.session.add(new_answer)
                    db.session.commit()
        elif questions_dump[i]['type'] in ['open']:
            submitted_answer = form[questions_dump[i]['id']]
            # if the user is_authenticated, update answer to the database for each choice selected
            if not submitted_answer:
                questions_dump[i]['missed'] = True
            else:
                questions_dump[i]['score'] = questions_dump[i]['point']
                questions_dump[i]['ans'] = submitted_answer
                cur_score += questions_dump[i]['point']
            if current_user.is_authenticated:
                new_answer = OpenAnswer(
                    user_id=current_user.id,
                    answer=submitted_answer,
                    question_id=questions_dump[i]['id'],
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
        elif questions_dump[i]['type'] in ['choose_many', 'grid_checkbox']:
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
        else:
            pass
        i += 1

    # if the user is authenticated, update final score to the database
    if current_user.is_authenticated:
        new_score = Score(
            score=cur_score,
            user_id=current_user.id,
            chapter_id=chapter_id
        )
        db.session.add(new_score)
        db.session.commit()

    ranking = get_ranking(chapter_id)
    return questions_dump, chapter_dump, cur_score, ranking


@bp.route('/quiz/<chapter_id>/submit', methods=['POST'])
def quiz_submit(chapter_id):
    """
    function for receiving quiz answers, checking them, store the score and return to the result page
    @param chapter_id: the chapter id for showing related quiz questions
    @type chapter_id: integer
    @return: return the quiz result page
    @rtype: flask template
    """

    questions_dump, chapter_dump, cur_score, ranking = store_quiz_results(chapter_id, request.form)

    return render_template("games/quiz_result.html", questions=questions_dump, cur_lvl=chapter_dump['level_id'],
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
        'select chapter.id, order_id, name, score, add_time, level_id from chapter left join score on score.chapter_id = chapter.id and score.user_id = %s order by chapter.id' % (current_user.id))

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
    if level_id == "3" and chapter_id == "4":
        return redirect(url_for('dnapi.paper_writing', ifFinished=True))
    cur_chapter_raw = db.engine.execute(
        'select * from chapter where level_id = %s and order_id = %s' % (level_id, chapter_id))
    cur_chapter = [dict(row) for row in cur_chapter_raw]
    chapter_dump, questions_dump = quiz_questions_helper(cur_chapter[0]['id'])
    selected_choices_raw = db.engine.execute(
        "select question.id as q_id,  choice.id as c_id from answer, chapter, choice, question where choice.question_id = question.id and question.chapter_id = chapter.id and choice.id = answer.choice_id and user_id = %s and chapter.id = %s order by question.id, choice.id" % (
            current_user.id, cur_chapter[0]['id']))
    ranking = get_ranking(cur_chapter[0]['id'])

    open_anwser_raw = db.engine.execute(
        'select question.id as q_id, answer as ans from open_answer, question, chapter where question.chapter_id = chapter.id and question.id = open_answer.question_id and user_id = %s and chapter.id = %s' % (current_user.id, cur_chapter[0]['id']))
    open_anwers = [dict(row) for row in open_anwser_raw]

    selected_choices = {}
    for row in selected_choices_raw:
        if str(row[0]) not in selected_choices:
            selected_choices[str(row[0])] = []
        selected_choices[str(row[0])].append(str(row[1]))

    score = Score.query.filter_by(user_id=current_user.id, chapter_id=cur_chapter[0]['id']).first()

    for question in questions_dump:
        if question['type'] in ['choose_one', 'grid', 'choose_many', 'grid_checkbox']:
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
        elif question['type'] in ['open']:
            for oa in open_anwers:
                if str(oa['q_id']) == str(question['id']):
                    question['ans'] = oa['ans']

    return render_template("games/quiz_result.html", questions=questions_dump, cur_lvl=level_id,
                           chapter=chapter_dump, score=score.score, ranking=ranking)


@bp.route('/galaxy_history')
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


def open_question_handler(form_data, chapter_id):
    """
    function for receiving paper answers, store the answers & scores and return to the result page
    @return: return the quiz result page
    @rtype: flask template
    """
    open_questions = {}
    left_data = {}
    for key, value in form_data.items():
        if key.startswith('open'):
            open_questions[key] = value
            q_key = key[4:]
            if q_key in form_data:
                open_questions[q_key] = form_data[q_key]

    for key, value in form_data.items():
        if key not in open_questions:
            left_data[key] = value

    questions = Question.query.filter_by(chapter_id=chapter_id, type="open").order_by(Question.id).all()
    # questions_dump = questionswithanswers_schema.dump(questions)
    # cur_chapter = Chapter.query.get(chapter_id)
    # chapter_dump = chapter_schema.dump(cur_chapter)
    #
    # if current_user.is_authenticated:
    #     for aws_id in submitted_answers:
    #         new_answer = Answer(
    #             user_id=current_user.id,
    #             choice_id=aws_id
    #         )
    #         db.session.add(new_answer)
    #         db.session.commit()
    #
    # # if the user is authenticated, update final score to the database
    # if current_user.is_authenticated:
    #     new_score = Score(
    #         score=cur_score,
    #         user_id=current_user.id,
    #         chapter_id=chapter_id
    #     )
    #     db.session.add(new_score)
    #     db.session.commit()
    return left_data


@bp.route('/paper_writing')
def paper_writing():
    """
    view function for paper writing page, getting value from previous chapters and showing them here.
    @return: return paper writing page
    @rtype: flask template
    """
    ifFinished = request.args.get("ifFinished")
    chapter = Chapter.query.filter_by(level_id=3, order_id=4).first()
    chapter_dump, questions_dump = quiz_questions_helper(chapter.id)
    if ifFinished == "False":
        introduction = 'Kombucha, a fermented beverage with roots tracing back over 2000 years to China, ' \
                'has gained worldwide popularity due to its purported health benefits (Jayabalan, ' \
                'Malbaša, Lončar, Vitas, & Sathishkumar, 2014). Over the years, extensive research ' \
                'has been conducted to understand its biochemical properties, microbiology, toxicity, ' \
                'cellulose production, and fermentation dynamics (Greenwalt, Steinkraus, & Ledford, 2000; ' \
                'Jayabalan et al., 2014; Rosma, Karim, & Bhat, 2012; Sreeramulu, Zhu, & Knol, 2000). ' \
                'The microbial diversity of Kombucha has been extensively studied using culture-based methods ' \
                'and sequencing of phylogenetic marker genes (Chakravorty et al., 2016; Coton et al., 2017; ' \
                'De Filippis, Troise, Vitaglione, & Ercolini, 2018; Marsh, O\'Sullivan, Hill, Ross, & Cotter, 2014; ' \
                'Reva et al., 2015). To build upon these findings, our study will leverage the Galaxy bioinformatics ' \
                'platform, a powerful, user-friendly, and open-source tool for the analysis and interpretation of ' \
                'genomic data. Our objective is to reanalyze the metagenomic data from two Turkish Kombucha samples, ' \
                'harvested at different stages of the fermentation process. We will employ WMS sequencing and ' \
                'NGS-based amplicon sequencing (16S rRNA gene and Internal Transcribed Spacer 1 [ITS1]) to derive ' \
                'detailed taxonomic and functional characteristics of the Kombucha samples. Through the Galaxy ' \
                'platform\'s robust suite of tools for genomic analysis, we aim to reaffirm the findings of the ' \
                'original study and potentially uncover additional insights into the microbial composition and ' \
                'functional dynamics of Kombucha. Our work illustrates the potent synergy of traditional microbiological ' \
                'studies and modern bioinformatics, paving the way for future explorations in this fascinating field.'
        results_answers_raw = db.engine.execute(
            'select question.transition_sentence as ts, answer as ans from open_answer, question where question.id = open_answer.question_id and user_id = %s and question.chapter_id = %s' % (
            current_user.id, chapter.id-1))
        results_answers = [dict(row) for row in results_answers_raw]
        results = ""
        for r in results_answers:
            results = results + r['ts'] + " "
            results = results + r['ans'] + " "
        methods_answers_raw = db.engine.execute(
            'select question.transition_sentence as ts, answer as ans from open_answer, question where question.id = open_answer.question_id and user_id = %s and question.chapter_id = %s' % (
            current_user.id, chapter.id-2))
        methods_answers = [dict(row) for row in methods_answers_raw]
        methods = ""
        for r in methods_answers:
            methods = methods + r['ts'] + " "
            methods = methods + r['ans'] + " "
        print(questions_dump)
        return render_template("games/level3/paper_writing.html", chapter=chapter_dump, questions=questions_dump,
                               methods=methods, results=results, introduction=introduction)
    else:
        open_anwser_raw = db.engine.execute(
            'select question.id as q_id, answer as ans from open_answer, question, chapter where question.chapter_id = chapter.id and question.id = open_answer.question_id and user_id = %s and chapter.id = %s' % (
            current_user.id, chapter.id))
        open_anwers = [dict(row) for row in open_anwser_raw]
        for question in questions_dump:
            for oa in open_anwers:
                if str(oa['q_id']) == str(question['id']):
                    question['ans'] = oa['ans']
        return render_template("games/level3/paper_writing.html", chapter=chapter_dump, questions=questions_dump)


@bp.route('/paper_writing/submit', methods=['POST'])
@login_required
def paper_writing_submit():
    """
        function for handling level 3 chapter 4 paper writing
        @return: return the quiz result page
        @rtype: flask template
    """
    store_quiz_results(12, request.form)
    return redirect(url_for('dnapi.paper_writing', ifFinished=True))

