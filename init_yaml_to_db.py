import yaml
import os
import pg_instance as pgdb
from db_config import DB_CONFIG
keys = ['title',
        'description',
        'type',
        'hint',
        'explanation',
        'image_url',
        'point',
        'chapter_id',
        # 'choices',
        # 'correct',
        ]

q_id = 23
c_id = 126


def parse_normal_question(q):
    global q_id
    tmp = [str(q_id)]
    # tmp = []
    q_id += 1
    for k in keys:
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


def show_json(file_path, data_dir, choice_dir):
    # os.remove(data_dir)
    with open(file_path, "r") as yaml_doc:
        yaml_to_dict = yaml.load(yaml_doc, Loader=yaml.FullLoader)
    q_csv = []
    c_csv = []
    for q in yaml_to_dict['questions']:
        if q['type'] in ['choose one', 'choose many']:
            q_csv.append(parse_normal_question(q))
            c_csv.extend(parse_normal_choices(q))
    try:
        with open(data_dir, "w") as out_file:
            for q in q_csv:
                out_file.write("%s\n" % q)
    except IOError as e:
        print("exception happened while transforming data files. (%s)" % e)
        return 1
    try:
        with open(choice_dir, "w") as out_file:
            for c in c_csv:
                out_file.write("%s\n" % c)
    except IOError as e:
        print("exception happened while transforming data files. (%s)" % e)
        return 1


def load_tables(host, port, db_name, user, password, table, out_dir):
    """Loads data into tables. Expects that tables are already empty.

    Args:
        data_dir (str): Directory in which load data exists
        host (str): IP/hostname of the PG instance
        port (int): port for the PG instance
        db_name (str): name of the tpch database
        user (str): user for the PG instance
        password (str): password for the PG instance
        table (str): list of tables
        out_dir (str): directory with data files to be loaded

    Return:
        0 if successful
        non zero otherwise
    """
    try:
        conn = pgdb.PGDB(host, port, db_name, user, password)
        try:
            filepath = os.path.join(out_dir)
            conn.copyFrom(filepath, separator="|", table=table)
            conn.commit()
            filepath = os.path.join('./quiz_db/level1/choices.csv')
            conn.copyFrom(filepath, separator="|", table='choice')
            conn.commit()
        except Exception as e:
            print("unable to run load tables. %s" %e)
            return 1
        conn.close()
        return 0
    except Exception as e:
        print("unable to connect to the database. %s" % e)
        return 1


if __name__ == '__main__':
    data_dir = './quiz_db/level1/chapter1.csv'
    choice_dir = './quiz_db/level1/choices.csv'
    file_p = './quiz_db/level1/chapter1.yaml'
    base_dir = './quiz_db/level1/'
    show_json(file_p, data_dir, choice_dir)
    host = "localhost"
    port = 5432
    table = 'question'
    if load_tables(host, port, DB_CONFIG['DB_NAME'], DB_CONFIG['USERNAME'], DB_CONFIG['PASSWORD'], table, data_dir):
        print("could not load data to tables")
        exit(1)
    print("done loading data to tables")