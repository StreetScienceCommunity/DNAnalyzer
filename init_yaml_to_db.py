import yaml

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

q_id = 1


def parse_normal_question(q):
    global q_id
    tmp = [str(q_id)]
    q_id += 1
    for k in keys:
        v = q[k]
        if v:
            v = str(v)
            if ',' in v:
                v = '"' + v + '"'
            tmp.append(v)
        else:
            tmp.append("")

    tmp = ",".join(tmp)
    return tmp.strip()


def parse_normal_choices(q):
    global q_id
    cur_id = str(q_id - 1)
    s = []
    for c in q['choices']:
        tmp = []
        for _, v in c.items():
            tmp.append(str(v))
        tmp.append(cur_id)
        tmp = ",".join(tmp)
        s.append(tmp.strip())
    return s


def show_json(file_path):
    with open(file_path, "r") as yaml_doc:
        yaml_to_dict = yaml.load(yaml_doc, Loader=yaml.FullLoader)
    q_csv = []
    c_csv = []
    for q in yaml_to_dict['questions']:
        if q['type'] in ['choose one', 'choose many']:
            q_csv.append(parse_normal_question(q))
            c_csv.extend(parse_normal_choices(q))
    for q in q_csv:
        print(q)
    for c in c_csv:
        print(c)




if __name__ == '__main__':
    file_p = './quiz_db/level1/chapter1.yaml'
    show_json(file_p)
