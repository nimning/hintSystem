DROP TABLE IF EXISTS {{course_name}}_realtime_past_answer;

CREATE TABLE {{course_name}}_realtime_past_answer (
    id int(11) NOT NULL AUTO_INCREMENT,
    set_id varchar(100) NOT NULL,
    problem_id varchar(100) NOT NULL,
    pg_id varchar(100) NOT NULL,
    user_id varchar(100) NOT NULL,
    source_file text,
    correct boolean,
    answer_string varchar(1024) DEFAULT NULL,
    difficulty varchar(100),
    timestamp TIMESTAMP,
    primary key (id)    
);
