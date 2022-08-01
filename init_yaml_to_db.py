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
        'chapter_id',
        # 'choices',
        # 'correct',
        ]

q_id = 1
c_id = 1


def parse_grid_question(q):
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
        tmp = "|".join(tmp)
        questions.append(tmp.strip())
        choices.extend(parse_grid_choices(q['choices'], descrip['answers']))
    return questions, choices


def parse_grid_choices(choices, answers):
    global q_id, c_id
    cur_id = str(q_id - 1)
    s = []
    for idx, c in choices.items():
        tmp = [str(c_id)]
        c_id += 1
        tmp.append(c)
        if idx in answers:
            tmp.append('true')
        else:
            tmp.append('false')
        tmp.append(cur_id)
        tmp = "|".join(tmp)
        s.append(tmp.strip())
    return s


def parse_normal_question(q):
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

    tmp = "|".join(tmp)
    return tmp.strip()


def parse_normal_choices(q):
    global q_id, c_id
    cur_id = str(q_id - 1)
    s = []
    for c in q['choices']:
        tmp = [str(c_id)]
        c_id += 1
        for _, v in c.items():
            tmp.append(str(v))
        tmp.append(cur_id)
        tmp = "|".join(tmp)
        s.append(tmp.strip())
    return s


def show_json(base_dir, chapter_id):
    """ wrapper function to convert yaml file to csv file
    Args:
        base_dir (str): directory with data files to be loaded
        chapter_id (str): chapter id
    """
    in_file = os.path.join(base_dir, 'chapter' + chapter_id + '.yaml')
    q_file = os.path.join(base_dir, 'chapter' + chapter_id + '.csv')
    c_file = os.path.join(base_dir, 'choices' + chapter_id + '.csv')
    with open(in_file, "r") as yaml_doc:
        yaml_to_dict = yaml.load(yaml_doc, Loader=yaml.FullLoader)
    q_csv = []
    c_csv = []
    for q in yaml_to_dict['questions']:
        if q['type'] in ['choose one', 'choose many']:
            q_csv.append(parse_normal_question(q))
            c_csv.extend(parse_normal_choices(q))
        if q['type'] in ['grid checkbox', 'grid']:
            tmp_q, tmp_c = parse_grid_question(q)
            q_csv.extend(tmp_q)
            c_csv.extend(tmp_c)
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


def clear_tables(host, port, db_name, user, password):
    """Empty the question and choice tables

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
        except Exception as e:
            print("unable to empty existing tables. %s" % e)
            return 1
        conn.close()
        return 0
    except Exception as e:
        print("unable to connect to the database. %s" % e)
        return 1


def load_tables(host, port, db_name, user, password, base_dir, chapter_id):
    """Loads data into tables. Expects that tables are already empty.

    Args:
        host (str): IP/hostname of the PG instance
        port (int): port for the PG instance
        db_name (str): name of the tpch database
        user (str): user for the PG instance
        password (str): password for the PG instance
        base_dir (str): directory with data files to be loaded
        chapter_id (str): chapter id
    Return:
        0 if successful
        non-zero otherwise
    """
    try:
        conn = pgdb.PGDB(host, port, db_name, user, password)
        try:
            q_file = os.path.join(base_dir, 'chapter' + chapter_id + '.csv')
            c_file = os.path.join(base_dir, 'choices' + chapter_id + '.csv')
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
    host = "localhost"
    port = 5432

    if clear_tables(host, port, DB_CONFIG['DB_NAME'], DB_CONFIG['USERNAME'], DB_CONFIG['PASSWORD']):
        print("could clear the tables")
        exit(1)
    print("successfully emptied database tables")

    for idx in range(1, 6):
        chapter_id = str(idx)
        level_dir = os.path.join(base_dir, 'chapter' + chapter_id)

        show_json(level_dir, chapter_id)

        if load_tables(host, port, DB_CONFIG['DB_NAME'], DB_CONFIG['USERNAME'],
                       DB_CONFIG['PASSWORD'], level_dir, chapter_id):
            print("could not load data to tables for chapter%s" % chapter_id)
            exit(1)
    print("successfully loaded data to tables")


if __name__ == '__main__':
    yaml_to_db()
