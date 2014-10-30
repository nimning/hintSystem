var App = angular.module('ta-console');

App.controller('ProblemPartCtrl', function($scope, $location, $window, $stateParams,
                                           $sce, $timeout, $interval, $anchorScroll, $modal, $log,
                                           WebworkService, HintsService, SockJSService, APIHost,
                                           DTOptionsBuilder, DTColumnDefBuilder, MessageService,
                                           Session){

    var course = $scope.course = $stateParams.course;
    var set_id = $scope.set_id = $stateParams.set_id;
    var problem_id = $scope.problem_id = $stateParams.problem_id;
    var part_id = $scope.part_id = $stateParams.part_id;
    var part_value = "AnSwEr"+("0000"+part_id).slice(-4);
    $scope.hint_id = -1;
    $scope.input_id = null;

    $scope.hints = [];
    angular.forEach(hints, function(value, key){
        $scope.hints.push(value);
    });

    WebworkService.answersByPart(course, set_id, problem_id).
        success(function(data){
            var answersByPart = {};
            angular.forEach(data, function(value){
                if (!answersByPart[value.part_id]){
                    answersByPart[value.part_id] = [];
                }
                answersByPart[value.part_id].push(value);
            });
            $scope.answers = answersByPart[part_id];
    });

    WebworkService.groupedPartAnswers(course, set_id, problem_id, part_id).success(function(data){
        $scope.grouped_answers = data.correct;
        $scope.shown_answers_array = [];
        angular.forEach($scope.grouped_answers, function(value,group){sort_answers(value,group);});
        $scope.correct_terms = data.correct_terms;
    }).error(function(data){
        $scope.grouped_answers = [];
        console.error(data);
        MessageService.addError('An error occurred while trying to group student answers.');
    });

    function sort_answers(value, group){
        var answer_object = {};
        answer_object["signature"] = group;
        answer_object["student_list"] = value;
        var student_set = [];
        //console.log(answer_object["student_list"]);
        for (v in value){
            var index = 0;
            for (s in value[v]) {
                console.log(value[v][s]);
                index = student_set.indexOf(value[v][s]);
                if (index == -1)
                    student_set.push(value[v][s]);
            }   
        }
        answer_object["sum"] = student_set.length;
        $scope.shown_answers_array.push(answer_object);
    }

    $scope.filter_terms = [];
    $scope.toggle_term = function(term){
        var idx = $scope.filter_terms.indexOf(term);
        if( ~idx ){
            $scope.filter_terms.splice(idx, 1);
        }else{
            $scope.filter_terms.push(term);
        }

        if($scope.filter_terms.length > 0){
            $scope.shown_answers_array = [];
            angular.forEach($scope.grouped_answers, function(value, group){
                if($scope.filter_terms.every(function(t){return group.indexOf(t)!=-1;})){
                    sort_answers(value, group);
                }
            });
        }else{
            $scope.shown_answers_array = [];
            angular.forEach($scope.grouped_answers, function(value, group){
                sort_answers(value, group);
            });
        }
    };

    $scope.term_selected = function(term){
        var idx = $scope.filter_terms.indexOf(term);
        return ~idx;
    };

    $scope.scrollTo = function($event) {
        $event.preventDefault();
        var id = $($event.target).attr('href').substr(1);
        var old = $location.hash();
        $location.hash(id);
        $anchorScroll();
        //reset to old to keep any additional routing logic from kicking in
        $location.hash(old);
    };

    WebworkService.problemPGPath(course, set_id, problem_id).success(function(data){
        $scope.pg_path = JSON.parse(data);
    });

    WebworkService.problemPGFile(course, set_id, problem_id).success(function(data){
        $scope.pg_file = JSON.parse(data);
        $scope.answer_expression = WebworkService.partSolution($scope.pg_file, part_id);
        var hf = WebworkService.extractHeaderFooter($scope.pg_file);
        $scope.pg_header = hf.pg_header;
        $scope.pg_footer = hf.pg_footer;

    });

    SockJSService.onMessage(function(event, data) {
        if (data.type === "my_students"){
            //$scope.my_students = data.arguments;
        }else if (data.type === "unassigned_students"){
            $scope.unassigned_students = data.arguments.filter(function(student){
                return student.problem_id == problem_id;
            });
        }
    });

    $scope.match_hint_id = function(id){
        var all_hints = $scope.hints;
        for (var i=0; i<all_hints.length; i++){
            if (all_hints[i].hint_id == id){
                $scope.hint_id = i;
                $scope.hint = all_hints[i];
                return all_hints[i].pg_text;
            }
        }
        $scope.hint_id = -1;
        return "no matching hint";
    };

    $scope.preview_send_hint = function(id, group){
        var students = [];
        for(var entry in group.student_list){ // For each different signature in the group
            for (var i=0; i<group.student_list[entry].length; i++){ //push student to the array
                var user_id = group.student_list[entry][i];
                var index = students.indexOf(user_id);
                if (index == -1)
                    students.push(user_id);
            }
        }

        for (i in students)
        {
            var hint_html_template = "";
            //$timeout(function(){
            // FIXME Put in the proper seed for the student
            HintsService.previewHint($scope.hint, 1234, true).
                then(function(student, rendered_html){
                    hint_html_template = rendered_html;
                    SockJSService.add_hint(course, set_id, problem_id, student,
                                           "AnSwEr"+("0000"+part_id).slice(-4), id, hint_html_template);
                    // the callback might execute after the end of the loop so we need to bind the value of student inside the loop
                }.bind(this, students[i]), function(error){
                    console.log(error);
                });
            //}, 1000);
        }
        this.input_id = null;
    };

    $scope.validID = function(){
        if ($scope.hint_id == -1)
            return false;
        else
            return true;
    };

    $scope.show_assigned_hints_by_student = function(student_id){
        var part_value = "AnSwEr"+("0000"+part_id).slice(-4);
        HintsService.assignedHintHistoryByStudentID(course, problem_id, set_id, student_id, part_value).
            success(function(data){
                hint.history = data;
                hint.students = [];
                for(h in data){
                    hint.students.push(data[h].hint_id);
                }
            }).error(function(data){console.log(data);});
    };

    WebworkService.problemPartStatus(course, set_id, problem_id, part_id).success(function(data){
        $scope.completion_data = data;
    });

    //student attempting statistics
    $scope.hint_static = [];
    $scope.attempting_student_list = [];
    $scope.struggling_student_list = [];
    $scope.trying_student_list = [];
    $scope.success_student_list = [];
    var attempting_student_list = [];
    var struggling_student_list = [];
    var trying_student_list = [];
    var success_student_list = [];

    function generate_hint_table() {
        WebworkService.answersByPart(course, set_id, problem_id).success(function(data){
            var answers_data = $scope.answers_data = data;
            var completed_student_list = [];
            var struggling_student_count = {};
            //push students who are attempting to the list
            for (s in answers_data) {
                if (answers_data[s].part_id == part_id) {
                    var local_user_id = answers_data[s].user_id;
                    if (answers_data[s].score == 0){
                        if (attempting_student_list.indexOf(local_user_id) == -1
                            && trying_student_list.indexOf(local_user_id) == -1
                            && struggling_student_list.indexOf(local_user_id) == -1) {
                            attempting_student_list.push(local_user_id);
                        }
                        if (!struggling_student_count[local_user_id])
                            struggling_student_count[local_user_id] = 1;
                        else
                            struggling_student_count[local_user_id]++;
                    }
                }
            }

            //push students who have more than 5 total attempts to struggling student list
            for (s in struggling_student_count){
                if (struggling_student_count[s] > 3
                    && struggling_student_list.indexOf(s) == -1
                    && trying_student_list.indexOf(s) == -1){
                    struggling_student_list.push(s);
                    var index = attempting_student_list.indexOf(s);
                    if (index != -1)
                        attempting_student_list.splice(index,1);
                }
            }

            //pop students who are done from attempting/struggling list
            for (s in answers_data) {
                if (answers_data[s].part_id == part_id && answers_data[s].score == 1) {
                    completed_student_list.push(answers_data[s].user_id);
                    var index = attempting_student_list.indexOf(answers_data[s].user_id);
                    if (index != -1) {
                        attempting_student_list.splice(index, 1);
                    }
                    index = struggling_student_list.indexOf(answers_data[s].user_id);
                    if (index != -1) {
                       struggling_student_list.splice(index, 1);
                    }
                }
            }

            //move students from attempting list to got hint list
            for (s in attempting_student_list) {
                HintsService.assignedHintHistoryByStudentID(course, problem_id, set_id, attempting_student_list[s], part_value).
                    success(function(data){
                        for (d in data) {
                            //add to trying student list
                            if (trying_student_list.indexOf(data[d].user_id) == -1)
                                trying_student_list.push(data[d].user_id);
                            //remove from attempting student list
                            var index = attempting_student_list.indexOf(data[d].user_id);
                            attempting_student_list.splice(index, 1);
                        }
                    });
            }

            //move students from struggling list to got hint list
            for (s in struggling_student_list) {
                HintsService.assignedHintHistoryByStudentID(course, problem_id, set_id, struggling_student_list[s], part_value).
                    success(function(data){
                        for (d in data) {
                            //add to trying student list
                            if (trying_student_list.indexOf(data[d].user_id) == -1)
                                trying_student_list.push(data[d].user_id);
                            // remove from struggling student list
                            var index = struggling_student_list.indexOf(data[d].user_id);
                            struggling_student_list.splice(index, 1);
                        }
                    });
            }

            //push to success student list
            for (c in completed_student_list) {
                HintsService.assignedHintHistoryByStudentID(course, problem_id, set_id, completed_student_list[c], part_value).
                    success(function(data){
                    if (data.length != 0 && success_student_list.indexOf(completed_student_list[c]) == -1)
                        success_student_list.push(completed_student_list[c]);
                    var index = trying_student_list.indexOf(completed_student_list[c]);
                    if (index != -1)
                        trying_student_list.splice(index,1);
                });
            }

            $scope.attempting_student_list = attempting_student_list;
            $scope.struggling_student_list = struggling_student_list;
            $scope.trying_student_list = trying_student_list;
            $scope.success_student_list = success_student_list;
        });
    }

    generate_hint_table();
    $interval(function(){generate_hint_table();}, 10000);

});
