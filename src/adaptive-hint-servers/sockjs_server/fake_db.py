class FakeDB:

    hints = {}
    answers = {}

    @staticmethod
    def get_hints(student_id, course_id, set_id, problem_id):
        hashkey = (student_id, course_id, set_id, problem_id)
        return FakeDB.hints.get(hashkey, [])
 
    @staticmethod
    def add_hint(student_id, course_id, set_id, problem_id, hint):
        hashkey = (student_id, course_id, set_id, problem_id)
        FakeDB.hints.setdefault(hashkey, []).append(hint)

    @staticmethod
    def remove_hint(student_id, course_id, set_id, problem_id,
                    location, hintbox_id):
        hashkey = (student_id, course_id, set_id, problem_id)
        hint_list = FakeDB.hints.get(hashkey, [])
        new_hint_list = [hint for hint in hint_list
                         if (hint['hintbox_id'] != hintbox_id or
                             hint['location'] != location)]
        FakeDB.hints[hashkey] = new_hint_list 
            
    @staticmethod
    def get_answers(student_id, course_id, set_id, problem_id):
        hashkey = (student_id, course_id, set_id, problem_id)
        return FakeDB.answers.get(hashkey, [])

    @staticmethod
    def add_answer(student_id, course_id, set_id, problem_id, answer_status):
        hashkey = (student_id, course_id, set_id, problem_id)
        FakeDB.answers.setdefault(hashkey, []).append(answer_status)

