from tornado_database import Connection
import os
import os.path
import json

mysql_username = "webworkWrite"
mysql_password = "webwork"

conn = Connection('localhost',
                  'webwork',
                  user=mysql_username,
                  password=mysql_password)
webwork_root = '/opt/webwork'

def export_problem(course, set_id, problem_id):
    """
    Problem PG file
    Traces of answer attempts, including hints given, for all students
    Hint collections
    """
    query = 'SELECT * from {0}_problem WHERE set_id = %s AND problem_id = %s'.format(course)
    result = conn.query(query, set_id, problem_id)[0]
    pg_path = result['source_file']
    with open(os.path.join(webwork_root, 'courses', course, 'templates', pg_path), 'r') as f:
        pg_file_contents = f.read()

    outfile = "{0}.json".format(pg_path)
    out = {}
    out['pg_file'] = pg_file_contents

    path = os.path.dirname(outfile)

    past_answers = conn.query(
        'SELECT * from {0}_past_answer where set_id = %s AND problem_id = %s'.format(course),
        set_id, problem_id)

    out['past_answers'] = past_answers

    realtime_past_answers = conn.query(
        'SELECT * from {0}_realtime_past_answer where set_id = %s AND problem_id = %s'.format(course),
        set_id, problem_id)

    out['realtime_past_answers'] = realtime_past_answers

    hints = conn.query(
        'SELECT * from {0}_hint where set_id = %s AND problem_id = %s'.format(course),
        set_id, problem_id)
    out['hints'] = hints

    assigned_hints = conn.query(
        'SELECT * from {0}_assigned_hint where set_id = %s AND problem_id = %s'.format(course),
        set_id, problem_id)
    out['assigned_hints'] = assigned_hints

    hint_feedback = conn.query(
        'SELECT {0}_assigned_hint_feedback.* from {0}_assigned_hint_feedback INNER JOIN {0}_assigned_hint ON {0}_assigned_hint_feedback.assigned_hint_id = {0}_assigned_hint.id WHERE {0}_assigned_hint.set_id = %s AND {0}_assigned_hint.problem_id = %s'.format(course),
        set_id, problem_id)
    out['hint_feedback'] = hint_feedback

    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        pass
    with open(outfile, 'w') as f:
        json.dump(out, f, indent=2)

if __name__ == '__main__':
    export_problem('CSE103', 'Assignment10.11.13', 1)
