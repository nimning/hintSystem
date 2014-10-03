from IPython.display import HTML
import requests
import pandas as pd

base_url='http://webwork.cse.ucsd.edu:4351/{action}'

def embed_problem(course, set_id, problem_id, seed=1234):
    """
    Renders a problem and returns an IPython widget for embedding
    """
    pg_path = requests.get(base_url.format(action='pg_path'), params={'course': course, 'set_id': set_id, 'problem_id': problem_id}).json()
    render = requests.post(base_url.format(action='render'), data={'pg_file': pg_path, 'seed': seed})
    response = render.json()
    return HTML(response['rendered_html'])

def get_attempts(course, set_id, problem_id):
        data = requests.get(base_url.format(action='answers_by_part'),params=
                         {'course':course, 'set_id':set_id, 'problem_id':problem_id}).json()
        df = pd.DataFrame(data)
        return df

def part_id_to_box(part_id):
    return "AnSwEr{part:04d}".format(part=part_id)

def get_correct_answers(course, set_id, problem_id, seed=1234):
    pg_path = requests.get(base_url.format(action='pg_path'),
                 params={'course':course, 'set_id':set_id, 'problem_id':problem_id}).json()
    check_answer = requests.post(base_url.format(action='checkanswer'),
                                 {'pg_file':pg_path, 'seed':seed, 'AnSwEr1':'0'}).json()
    return {k: v['correct_value'] for k, v in check_answer.iteritems()}
