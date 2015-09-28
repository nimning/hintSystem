var App = angular.module('ta-console');

App.value('APIPort', 4351);
App.value('APIHost', 'webwork.cse.ucsd.edu');

App.value('CurrentCourse', {name: 'Course'});

App.value('user_id_for_problem_render', 'pg_render');
App.value('password_for_problem_render', 'pgrender');

App.constant(
    'HintFilterProperties', {
        regex_match_filter: {
            name: 'Regex Match Filter',
            description: "Returns true if the student's submission matches the"+
                " provided regular expression.",
            takesArg: true
        },
        expression_value_filter: {
            name: 'Expression Value Filter',
            description: "Takes as argument one or more mathematical expressions"+
                " whose presence will be tested for. Expressions must be preceded"+
                " with either the string <code>HAS</code> or <code>MISSING</code>"+
                " to denote whether the"+
                " filter should trigger on the presence or absence of the value"+
                " of the expression in the student's answer. Expressions can be"+
                " combined by placing a <code>&</code> between expressions.\n\n" +
                " For example, the condition <code>HAS 8*4 & MISSING C(8*4, 5)</code> would"+
                " trigger if the student's answer contained the value <var>8*4</var> but was"+
                " missing the value <var>C(8*4,5)</var>."+
                "\n\nNote: Does not yet support randomized constants.",
            takesArg: true
        },
        struggling_student_filter:{
            name: "Struggling Student Filter",
            description: "Returns true if the student has been attempting the problem for some time",
            takesArg: false
        }

    });

App.value('angularMomentConfig', {
    timezone: 'America/Los_Angeles' // optional
});
