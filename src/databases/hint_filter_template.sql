DROP TABLE IF EXISTS {{course_name}}_assigned_hint_filter;
DROP TABLE IF EXISTS {{course_name}}_hint_filter;

CREATE TABLE {{course_name}}_hint_filter (
    id int NOT NULL AUTO_INCREMENT,
    filter_name varchar(255) NOT NULL,

    primary key (id)
);

CREATE TABLE {{course_name}}_assigned_hint_filter (
    hint_id int NOT NULL,
    -- Which hint filter:
    hint_filter_id int NOT NULL,
    -- When the hint was assigned:
    assigned TIMESTAMP,
    trigger_cond TEXT,
    primary key (hint_id, hint_filter_id),
    CONSTRAINT FOREIGN KEY (hint_id) REFERENCES {{course_name}}_hint(id),
    CONSTRAINT FOREIGN KEY (hint_filter_id) REFERENCES {{course_name}}_hint_filter(id)
);
