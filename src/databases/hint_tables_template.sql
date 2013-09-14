DROP TABLE IF EXISTS CompoundProblems_hint;
DROP TABLE IF EXISTS CompoundProblems_assigned_hint;
DROP TABLE IF EXISTS CompoundProblems_hint_attempt;

CREATE TABLE {{course_name}}_hint (
    id int NOT NULL,
    pg_id int NOT NULL,
    problem_id int NOT NULL,
    pg_text varchar(65536) NOT NULL,
    CONSTRAINT FOREIGN KEY (problem_id) REFERENCES {{course_name}}_problem(problem_id),
    primary key (id)
);

CREATE TABLE {{course_name}}_assigned_hint (
    hint_id int NOT NULL,
    user_id int NOT NULL,
    CONSTRAINT FOREIGN KEY (hint_id) REFERENCES {{course_name}}_hint(id),
    CONSTRAINT FOREIGN KEY (user_id) REFERENCES {{course_name}}_user(user_id)
);

CREATE TABLE {{course_name}}_hint_attempt (
    hint_id int NOT NULL,
    user_id int NOT NULL,
    correct BOOLEAN,
    expression varchar(65536) NOT NULL,
    timestamp TIMESTAMP,
    CONSTRAINT FOREIGN KEY (hint_id) REFERENCES {{course_name}}_hint(id),
    CONSTRAINT FOREIGN KEY (user_id) REFERENCES {{course_name}}_user(user_id)
);
