var App = angular.module('ta-console');

App.factory('WebworkService', function($http, $window, $rootScope, $location, $q, APIHost, APIPort) {
    var BASE_URL = 'http://'+APIHost+':'+APIPort;
    var factory = {
        sets: function(course, fn) {
            $http
                .get(BASE_URL+'/sets',
                     {params: {course: course}})
                .success(function (data, status, headers, config) {
                    fn(data);
                });
        },
        problems: function(course, set_id) {
            return $http
                .get(BASE_URL+'/problems',
                     {params: {course: course, set_id: set_id}});
        },
        problemHints: function(course, set_id, problem_id) {
            return $http
                .get(BASE_URL+'/problem_hints',
                     {params: {course: course, set_id: set_id, problem_id: problem_id}});
        },
        exportProblemData: function(course, set_id, problem_id) {
            return $http
                .get(BASE_URL+'/export_problem_data',
                     {params: {course: course, set_id: set_id, problem_id: problem_id}});
        },
        problemPGFile: function(course, set_id, problem_id) {
            return $http
                .get(BASE_URL+'/pg_file',
                     {params: {course: course, set_id: set_id, problem_id: problem_id}});
        },
        problemPGPath: function(course, set_id, problem_id) {
            return $http
                .get(BASE_URL+'/pg_path',
                     {params: {course: course, set_id: set_id, problem_id: problem_id}});
	},
        problemSeed: function(course, set_id, problem_id, user_id) {
            return $http
                .get(BASE_URL+'/problem_seed',
                     {params: {course: course, set_id: set_id,
                               problem_id: problem_id, user_id: user_id}});
        },
        setPsvn: function(course, set_id, user_id) {
            return $http
                .get(BASE_URL+'/set_psvn',
                     {params: {course: course, set_id: set_id, user_id: user_id}});
        },

        answersByPart: function(course, set_id, problem_id, user_id, counts) {
            return $http
                .get(BASE_URL+'/answers_by_part',
                     {params: {course: course, set_id: set_id, problem_id: problem_id,
                               user_id: user_id, counts: counts}});
        },
        answersByPartCounts: function(course, set_id, problem_id, user_id) {
            return $http
                .get(BASE_URL+'/answers_by_part',
                     {params: {course: course, set_id: set_id, problem_id: problem_id,
                               user_id: user_id, counts: true}});
        },
        render: function(pg_file, seed, psvn) {
            if(pg_file[0]!=='/'){ // Don't base64 encode absolute paths
                pg_file = btoa(unescape(encodeURIComponent(pg_file)));
            }
            return $http
                .post(BASE_URL+'/render',
                      {pg_file: pg_file, seed: seed.toString(), psvn: psvn});
        },
        checkAnswer: function(pg_file, seed, answers) {
            if(pg_file[0]!=='/'){ // Don't base64 encode absolute paths
                pg_file = btoa(unescape(encodeURIComponent(pg_file)));
            }
            return $http
                .post(BASE_URL+'/checkanswer',
                      angular.extend({pg_file: pg_file, seed: seed.toString()}, answers)
                     );
        },
        extractHeaderFooter: function(pg_text) {
            var re_header = /^[\s]*(TEXT\(PGML|BEGIN_PGML)[\s]+/gm;
	        var re_footer = /^[\s]*END_PGML[\s]+/gm;
	        var pg_header = re_header.exec(pg_text);
	        var pg_footer = re_footer.exec(pg_text);
	        if (pg_header && pg_footer) {
	            // reconstruct the footer
	            pg_header = pg_text.substr(0, pg_header.index) + '\nBEGIN_PGML\n';
	            pg_footer = pg_text.substr(pg_footer.index);
	            // Remove Solution section
	            pg_footer = pg_footer.replace(/^(BEGIN_PGML_SOLUTION|BEGIN_PGML_HINT)[\s\S]*END_PGML_SOLUTION/m,'');
	        }
            return {
                pg_header: pg_header,
                pg_footer: pg_footer
            };

        },
        parseString: function(expression) {
            return $http
                .post(BASE_URL+'/parse_string',
                     {expression: expression});
        },
        groupedPartAnswers: function(course, set_id, problem_id, part_id) {
            return $http
                .get(BASE_URL+'/grouped_part_answers',
                     {params: {course: course, set_id: set_id, problem_id: problem_id,
                     part_id: part_id}});
        },
        problemStatus: function(course, set_id, problem_id) {
            return $http
                .get(BASE_URL+'/problem_status',
                     {params: {course: course, set_id: set_id, problem_id: problem_id}});
        },
        problemPartStatus: function(course, set_id, problem_id, part_id) {
            return $http
                .get(BASE_URL+'/problem_part_status',
                     {params: {course: course, set_id: set_id, problem_id: problem_id,
                     part_id: part_id}});
        },
        partSolution: function(pg_file, part_id){
            // Look for [__] followed by {} with either a Compute("")
            // call inside or just a normal mathematical expression.
            var re = /\[__+\]{(?:(?:Compute\(")?(.+?)(?:"\))(?:.*)?|(.+?))}/g;
            var i = 0;
            var match;
            while(i < part_id){
                match = re.exec(pg_file);
                i++;
            }
            // group 1 is with Compute(""), group 2 is without
            if(match && (match[1] || match[2])){
                return match[1] || match[2];
            }else{
                return '';
            }
        },
        partCount: function(pg_file) {
            var box_re = /\[__+\]/g;
            var box_matches = pg_file.match(box_re);
            var box_count = box_matches ? box_matches.length : 0;
            var ans_re = /ANS\(.+\)/g;
            var ans_matches = pg_file.match(ans_re);
            var ans_count = ans_matches ? ans_matches.length : 0;
            return box_count + ans_count;
        },
        partIdToBoxName: function(part_id){
            return "AnSwEr"+("0000"+part_id).slice(-4);
        },
        filterAnswers: function(course, set_id, problem_id, part_id, filter_function){
            return $http
                .post(BASE_URL+'/filter_answers',
                      {course: course, set_id: set_id, problem_id: problem_id,
                       part_id: part_id, filter_function: filter_function});
        }
    };
    return factory;
});
