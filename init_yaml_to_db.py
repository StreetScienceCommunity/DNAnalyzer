import collections

import yaml
import os
import pg_instance as pgdb
from db_config import DB_CONFIG

keys = ['title',
        'description',
        'type',
        'hint',
        'explanation',
        'image_name',
        'point',
        # 'chapter_id',
        # 'choices',
        # 'correct',
        ]

levels = [
    'Sam the alien',
    'BeerDEcoded',
    'Peer review'
]

q_id = 1
choice_id = 1
chapter_id_overall = 1


def int_to_string_helper(s):
    if s is None:
        return ""
    else:
        return str(s)


def parse_grid_question(q, chapter_id):
    global q_id
    questions, choices = [], []
    descrips = q['questions']
    for descrip in descrips:
        tmp = [str(q_id)]
        q_id += 1
        for k in keys:
            v = ''
            if k in q:
                v = q[k]
            if v:
                v = str(v)
                if '|' in v:
                    v = '"' + v + '"'
                tmp.append(v)
            else:
                tmp.append("")
        tmp[2] = descrip['text']
        tmp.append(chapter_id)
        tmp = "|".join(tmp)
        questions.append(tmp.strip())
        choices.extend(parse_grid_choices(q['choices'], descrip['answers']))
    return questions, choices


def parse_grid_choices(choices, answers):
    global q_id, choice_id
    cur_id = str(q_id - 1)
    s = []
    for idx, c in choices.items():
        tmp = [str(choice_id)]
        choice_id += 1
        tmp.append(c)
        if idx in answers:
            tmp.append('true')
        else:
            tmp.append('false')
        tmp.append(cur_id)
        tmp = "|".join(tmp)
        s.append(tmp.strip())
    return s


def parse_normal_question(q, chapter_id):
    global q_id
    tmp = [str(q_id)]
    q_id += 1
    for k in keys:
        v = ''
        if k in q:
            v = q[k]
        if v:
            v = str(v)
            if '|' in v:
                v = '"' + v + '"'
            tmp.append(v)
        else:
            tmp.append("")
    tmp.append(chapter_id)
    tmp = "|".join(tmp)
    return tmp.strip()


def parse_normal_choices(q):
    global q_id, choice_id
    cur_id = str(q_id - 1)
    s = []
    for c in q['choices']:
        tmp = [str(choice_id)]
        choice_id += 1
        for _, v in c.items():
            tmp.append(str(v))
        tmp.append(cur_id)
        tmp = "|".join(tmp)
        s.append(tmp.strip())
    return s


def parse_chapter(q, chapter_id):
    global q_id
    tmp = [str(q_id)]
    q_id += 1
    for k in keys:
        v = ''
        if k in q:
            v = q[k]
        if v:
            v = str(v)
            if '|' in v:
                v = '"' + v + '"'
            tmp.append(v)
        else:
            tmp.append("")
    tmp.append(chapter_id)
    tmp = "|".join(tmp)
    return tmp.strip()


def show_json(base_dir, chapter_id, cur_lvl):
    """ wrapper function to convert yaml file to csv file
    Args:
        base_dir (str): directory with data files to be loaded
        chapter_id (str): chapter id
    """
    global chapter_id_overall
    in_file = os.path.join(base_dir, 'quiz' + '.yaml')
    q_file = os.path.join(base_dir, 'questions' + '.csv')
    c_file = os.path.join(base_dir, 'choices' + '.csv')
    chapter_file = os.path.join(base_dir, 'chapter' + '.csv')

    with open(in_file, "r") as yaml_doc:
        yaml_to_dict = yaml.load(yaml_doc, Loader=yaml.FullLoader)

    q_csv = []
    c_csv = []

    chapter_csv = str(chapter_id_overall) + '|' \
                  + int_to_string_helper(yaml_to_dict['total_score']) + '|' \
                  + str(cur_lvl) + '|' + \
                  int_to_string_helper(yaml_to_dict['video_url']) + '|' \
                  + int_to_string_helper(yaml_to_dict['chapter_name']) + '|' \
                  + str(chapter_id)

    if yaml_to_dict['questions']:
        for q in yaml_to_dict['questions']:
            if q['type'] in ['choose_one', 'choose_many']:
                q_csv.append(parse_normal_question(q, str(chapter_id_overall)))
                c_csv.extend(parse_normal_choices(q))
            if q['type'] in ['open']:
                q_csv.append(parse_normal_question(q, str(chapter_id_overall)))
            if q['type'] in ['grid_checkbox', 'grid']:
                tmp_q, tmp_c = parse_grid_question(q, str(chapter_id_overall))
                q_csv.extend(tmp_q)
                c_csv.extend(tmp_c)

    chapter_id_overall += 1

    try:
        with open(chapter_file, "w") as out_file:
            out_file.write("%s\n" % chapter_csv)
    except IOError as e:
        print("exception happened while transforming data files. (%s)" % e)
        return 1

    try:
        with open(q_file, "w") as out_file:
            for q in q_csv:
                out_file.write("%s\n" % q)
    except IOError as e:
        print("exception happened while transforming data files. (%s)" % e)
        return 1

    try:
        with open(c_file, "w") as out_file:
            for c in c_csv:
                out_file.write("%s\n" % c)
    except IOError as e:
        print("exception happened while transforming data files. (%s)" % e)
        return 1


def process_level(base_dir, host, port, db_name, user, password):
    """ wrapper function to convert yaml file to csv file
    Args:
        base_dir (str): directory with data files to be loaded
        chapter_id (str): chapter id
    """
    levels_file = os.path.join(base_dir, 'levels' + '.csv')

    lvl_csv = []
    for index, item in enumerate(levels, start=1):
        tmp = str(index) + '|' + item
        lvl_csv.append(tmp.strip())

    try:
        with open(levels_file, "w") as out_file:
            for l in lvl_csv:
                out_file.write("%s\n" % l)
    except IOError as e:
        print("exception happened while transforming data files. (%s)" % e)
        return 1

    try:
        conn = pgdb.PGDB(host, port, db_name, user, password)
        try:
            conn.copyFrom(levels_file, separator="|", table='level')
            conn.commit()
            os.remove(levels_file)
        except Exception as e:
            print("unable to run load tables. %s" % e)
            return 1
        conn.close()
        return 0
    except Exception as e:
        print("unable to connect to the database. %s" % e)
        return 1


def clear_tables(host, port, db_name, user, password):
    """Empty the chapters, question and choice tables

    Args:
        host (str): IP/hostname of the PG instance
        port (int): port for the PG instance
        db_name (str): name of the tpch database
        user (str): user for the PG instance
        password (str): password for the PG instance

    Return:
        0 if successful
        non-zero otherwise
    """
    try:
        conn = pgdb.PGDB(host, port, db_name, user, password)
        try:
            conn.executeQuery("DELETE FROM choice")
            conn.commit()
            conn.executeQuery("DELETE FROM question")
            conn.commit()
            conn.executeQuery("DELETE FROM chapter")
            conn.commit()
            conn.executeQuery("DELETE FROM level")
            conn.commit()
        except Exception as e:
            print("unable to empty existing tables. %s" % e)
            return 1
        conn.close()
        return 0
    except Exception as e:
        print("unable to connect to the database. %s" % e)
        return 1


def load_tables(host, port, db_name, user, password, base_dir):
    """Loads data into tables. Expects that tables are already empty.

    Args:
        host (str): IP/hostname of the PG instance
        port (int): port for the PG instance
        db_name (str): name of the tpch database
        user (str): user for the PG instance
        password (str): password for the PG instance
        base_dir (str): directory with data files to be loaded
    Return:
        0 if successful
        non-zero otherwise
    """
    try:
        conn = pgdb.PGDB(host, port, db_name, user, password)
        try:
            chapter_file = os.path.join(base_dir, 'chapter' + '.csv')
            q_file = os.path.join(base_dir, 'questions' + '.csv')
            c_file = os.path.join(base_dir, 'choices' + '.csv')
            conn.copyFrom(chapter_file, separator="|", table='chapter')
            conn.commit()
            os.remove(chapter_file)
            conn.copyFrom(q_file, separator="|", table='question')
            conn.commit()
            os.remove(q_file)
            conn.copyFrom(c_file, separator="|", table='choice')
            conn.commit()
            os.remove(c_file)
        except Exception as e:
            print("unable to run load tables. %s" % e)
            return 1
        conn.close()
        return 0
    except Exception as e:
        print("unable to connect to the database. %s" % e)
        return 1


def yaml_to_db():
    base_dir = 'game/'
    max_lvl = 0
    lvl_dict = {}
    global q_id, choice_id, chapter_id_overall

    # iterate through game folder, find max level and max chapter for each level
    for lvl_folder in os.scandir(base_dir):
        if os.path.isdir(lvl_folder) and lvl_folder.name.startswith("level"):
            cur_lvl = int(lvl_folder.name[5:])
            max_lvl = max(cur_lvl, max_lvl)
            max_chap = 0
            for chapter_folder in os.scandir(base_dir+'/'+lvl_folder.name+'/'):
                if chapter_folder.name.startswith("chapter"):
                    max_chap = max(int(chapter_folder.name[7:]), max_chap)
            lvl_dict[cur_lvl] = max_chap
    lvl_dict = collections.OrderedDict(sorted(lvl_dict.items()))

    # clear level chapter and choice tables in the database
    if clear_tables(DB_CONFIG['DB_HOST'], DB_CONFIG['DB_PORT'], DB_CONFIG['DB_NAME'], DB_CONFIG['USERNAME'], DB_CONFIG['PASSWORD']):
        print("could clear the tables")
        exit(1)
    print("successfully emptied database tables")

    # load all levels to the database first
    if process_level(base_dir, DB_CONFIG['DB_HOST'], DB_CONFIG['DB_PORT'], DB_CONFIG['DB_NAME'], DB_CONFIG['USERNAME'], DB_CONFIG['PASSWORD']):
        print("could process levels")
        exit(1)
    print("successfully loaded data for level table")

    # iterate through each chapter folder to parse yaml file to json and load them to the database
    for cur_lvl in range(1, max_lvl+1):
        level_dir = os.path.join(base_dir, 'level' + str(cur_lvl))
        for idx in range(1, lvl_dict[cur_lvl]+1):
            chapter_id = str(idx)
            chapter_dir = os.path.join(level_dir, 'chapter' + chapter_id)
            show_json(chapter_dir, chapter_id, cur_lvl)
            if load_tables(DB_CONFIG['DB_HOST'], DB_CONFIG['DB_PORT'], DB_CONFIG['DB_NAME'], DB_CONFIG['USERNAME'],
                           DB_CONFIG['PASSWORD'], chapter_dir):
                print("could not load data to tables for chapter%s" % chapter_id)
                exit(1)
    print("successfully loaded data to tables")


if __name__ == '__main__':
    yaml_to_db()
