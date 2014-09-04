DROP TABLE IF EXISTS {{course_name}}_hint;
DROP TABLE IF EXISTS {{course_name}}_assigned_hint;
DROP TABLE IF EXISTS {{course_name}}_assigned_hint_feedback;

CREATE TABLE {{course_name}}_hint (
    id int NOT NULL AUTO_INCREMENT,
    pg_text varchar(65536) NOT NULL,
    author varchar(255) NOT NULL,
    set_id varchar(255) NOT NULL,
    problem_id int NOT NULL,
    created TIMESTAMP,
    deleted boolean default false,

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
    hint_html text NOT NULL,

    primary key (id),
    CONSTRAINT FOREIGN KEY (hint_id) REFERENCES {{course_name}}_hint(id)
);

CREATE TABLE {{course_name}}_assigned_hint_feedback (
    assigned_hint_id int NOT NULL,
    feedback varchar(255) NOT NULL,
    timestamp TIMESTAMP,
    CONSTRAINT FOREIGN KEY (assigned_hint_id) REFERENCES {{course_name}}_assigned_hint(id)
);
