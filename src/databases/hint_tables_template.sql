DROP TABLE IF EXISTS {{course_name}}_hint;
DROP TABLE IF EXISTS {{course_name}}_assigned_hint;
DROP TABLE IF EXISTS {{course_name}}_hint_attempt;

CREATE TABLE {{course_name}}_hint (
    id int NOT NULL AUTO_INCREMENT,
    pg_text varchar(65536) NOT NULL,
    author varchar(255) NOT NULL,
    created TIMESTAMP, 

    primary key (id)
);

CREATE TABLE {{course_name}}_assigned_hint (
    id int NOT NULL AUTO_INCREMENT,
    -- Where:
    set_id varchar(255) NOT NULL,
    problem_id int NOT NULL,
    pg_id varchar(255) NOT NULL,
    -- Who:
    user_id varchar(255) NOT NULL,
    -- Which hint:
    hint_id int NOT NULL,
    -- When the hint was assigned:
    assigned TIMESTAMP,

    primary key (id)
);

CREATE TABLE {{course_name}}_hint_attempt (
    id int NOT NULL AUTO_INCREMENT,
    assigned_hint int NOT NULL, -- id field of ..._assigned_hint
    correct BOOLEAN NOT NULL,
    expression varchar(65536) NOT NULL,
    -- When the student attempted the hint:
    timestamp TIMESTAMP,

    primary key (id)
);
