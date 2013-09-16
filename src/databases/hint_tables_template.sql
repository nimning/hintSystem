DROP TABLE IF EXISTS CompoundProblems_hint;
DROP TABLE IF EXISTS CompoundProblems_assigned_hint;
DROP TABLE IF EXISTS CompoundProblems_hint_attempt;

CREATE TABLE {{course_name}}_hint (
    id int NOT NULL AUTO_INCREMENT,
    pg_id varchar(255) NOT NULL,
    problem_id int NOT NULL,
    set_id varchar(255) NOT NULL,
    pg_text varchar(65536) NOT NULL,
    timestamp TIMESTAMP, 
    CONSTRAINT FOREIGN KEY (problem_id) REFERENCES {{course_name}}_problem(problem_id),
    CONSTRAINT FOREIGN KEY (set_id) REFERENCES {{course_name}}_problem(set_id),
    primary key (id)
);

CREATE TABLE {{course_name}}_assigned_hint (
    hint_id int NOT NULL,
    user_id varchar(255) NOT NULL,
    timestamp TIMESTAMP,
    CONSTRAINT FOREIGN KEY (hint_id) REFERENCES {{course_name}}_hint(id),
    CONSTRAINT FOREIGN KEY (user_id) REFERENCES {{course_name}}_user(user_id)
);

CREATE TABLE {{course_name}}_hint_attempt (
    hint_id int NOT NULL,
    user_id varchar(255) NOT NULL,
    correct BOOLEAN NOT NULL,
    expression varchar(65536) NOT NULL,
    timestamp TIMESTAMP,
    CONSTRAINT FOREIGN KEY (hint_id) REFERENCES {{course_name}}_hint(id),
    CONSTRAINT FOREIGN KEY (user_id) REFERENCES {{course_name}}_user(user_id)
);
