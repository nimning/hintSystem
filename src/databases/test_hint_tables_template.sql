insert into {{course_name}}_hint (pg_text, author) values ("This might help: what is 1+1?  [____]{2}", "melkherj");
insert into {{course_name}}_assigned_hint (set_id, problem_id, user_id, pg_id, hint_id) values ("compoundProblemExperiments", 1, "melkherj", "a", LAST_INSERT_ID());
insert into {{course_name}}_hint (pg_text, author) values ("This might help: what is 2+2?  [____]{4}", "melkherj");
insert into {{course_name}}_assigned_hint (set_id, problem_id, user_id, pg_id, hint_id) values ("compoundProblemExperiments", 1, "melkherj", "b", LAST_INSERT_ID());
