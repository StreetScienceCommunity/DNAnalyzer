import yaml


def show_json(file_path):
    with open(file_path, "r") as yaml_doc:
        yaml_to_dict = yaml.load(yaml_doc, Loader=yaml.FullLoader)
    q_csv = []
    for q in yaml_to_dict['questions']:
        tmp = []
        for k, v in q.items():
            if k not in ['choices', 'correct']:
                if v:
                    v = str(v)
                    if ',' in v:
                        v = '"' + v + '"'
                    tmp.append(v)
                else:
                    tmp.append("")

        tmp = ",".join(tmp)
        q_csv.append(tmp.strip())
    for s in q_csv:
        print(s, "\n")


if __name__ == '__main__':
    file_p = './quiz_db/level1/chapter1.yaml'
    show_json(file_p)
