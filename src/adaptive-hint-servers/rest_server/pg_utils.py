from process_query import conn
from webwork_config import webwork_dir
import re
import os


def get_source(course, set_id, problem_id):
    source_file = conn.query('''select source_file from {course}_problem
            where problem_id={problem_id} and set_id="{set_id}";
        '''.format(course=course, set_id=set_id, problem_id=problem_id))[0]['source_file']
    pg_path = os.path.join(webwork_dir, 'courses', course, 'templates', source_file)
    with open(pg_path, 'r') as fin:
        pg_file = fin.read()
        return pg_file


def get_part_answer(pg_file, part_id):
    # Matches answers with Compute() and without in separate groups
    answer_re = re.compile('\[__+\]{(?:(?:Compute\(")(.+?)(?:"\))(?:.*)|(.+?))}')
    answer_boxes = answer_re.findall(pg_file)
    if part_id < len(answer_boxes):
        part_answer = answer_boxes[part_id-1][0] or answer_boxes[part_id-1][1]
    else:
        part_answer = ''
    return part_answer
