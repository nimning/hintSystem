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
    $scope.linked_hint = null;
    $scope.showFilterFunction = true;
    $scope.showGroups = true;
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
        var pg_file = JSON.parse(data);
        /*console.log(pg_file);
        var expr = /BEGIN_PGML\[(\$.)\](.+)(END_PGML)/g;
        var match = expr.exec(pg_file);
        console.log(match);
        var new_pg_file = pg_file;
        var added_index = 0;
        while (match) {
            var i = match.index+match[0].length+added_index;
            var s = ['\\[',match[1],'\\]'].join('');
            new_pg_file = [new_pg_file.slice(0,i),s,new_pg_file.slice(i)].join('');
            added_index = added_index+match[0].length+2;
            match = expr.exec(pg_file);
        }
        */
        $scope.pg_file = pg_file;
        $scope.answer_expression = WebworkService.partSolution($scope.pg_file, part_id);
        WebworkService.checkAnswer($scope.pg_file, 1234, {AnSwEr1:1}).success(function(answer){
            $scope.answer_value = answer[part_value].correct_value;
        });
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
        if (id == null)
            return;
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

    $scope.link_hint = function(id, group){
        //link hint to group here
        this.linked_hint=this.hint.pg_text;
        this.input_id = null;
    };

    $scope.remove_linked_hint = function(){
        //remove linked hint
        this.linked_hint=null;
    }

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

        for (i=0; i <students.length; i++)
        {
            var hint_html_template = "";
            $timeout(function(student){ // Render with a random delay.
                // FIXME Put in the proper seed for the student
                HintsService.previewHint($scope.hint, 1234, true).
                    then(function(rendered_html){
                        hint_html_template = rendered_html;
                        SockJSService.add_hint(course, set_id, problem_id, student,
                                               "AnSwEr"+("0000"+part_id).slice(-4), id, hint_html_template);
                        // the callback might execute after the end of the loop so we need to bind the value of student inside the loop
                    }, function(error){
                        console.log(error);
                    });
            }.bind(this, students[i]), 2000*Math.random());
        }
        this.input_id = null;
    };

    $scope.validID = function(){
        if ($scope.hint_id == -1)
            return false;
        else
            return true;
    };

    $scope.validLink = function(){
        if (this.linked_hint != null)
            return true;
        else
            return false;
    };

    /*$scope.show_assigned_hints_by_student = function(student_id){
        var part_value = "AnSwEr"+("0000"+part_id).slice(-4);
        HintsService.assignedHintHistoryByStudentID(course, problem_id, set_id, student_id, part_value).
            success(function(data){
                hint.history = data;
                hint.students = [];
                for(h in data){
                    hint.students.push(data[h].hint_id);
                }
            }).error(function(data){console.log(data);});
    };*/

    $scope.get_student_hint_history = function(){
        var student_hint_history = {};
        HintsService.assignedHintHistoryByProblemPart(course, problem_id, set_id, part_value).success(function(data){
            for (d in data) {
                if (!student_hint_history[data[d].user_id])
                    student_hint_history[data[d].user_id] = [];
                student_hint_history[data[d].user_id].push(data[d]);
            }
        });
        return student_hint_history;
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
            var student_hint_history = {};

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

            HintsService.assignedHintHistoryByProblemPart(course, problem_id, set_id, part_value).success(function(data){
                for (d in data) {
                    if (!student_hint_history[data[d].user_id])
                        student_hint_history[data[d].user_id] = [];
                    student_hint_history[data[d].user_id].push(data[d]);
                }

                //move students from attempting list to got hint list
                angular.forEach(attempting_student_list, function(student) {
                    var data = student_hint_history[student];
                    for (d in data) {
                        //add to trying student list
                        if (trying_student_list.indexOf(data[d].user_id) == -1)
                            trying_student_list.push(data[d].user_id);
                        //remove from attempting student list
                        var index = attempting_student_list.indexOf(data[d].user_id);
                        attempting_student_list.splice(index, 1);
                    }
                });

                //move students from struggling list to got hint list
                angular.forEach(struggling_student_list, function(student) {
                    var data = student_hint_history[student];
                    for (d in data) {
                        //add to trying student list
                        if (trying_student_list.indexOf(data[d].user_id) == -1)
                            trying_student_list.push(data[d].user_id);
                        // remove from struggling student list
                        var index = struggling_student_list.indexOf(data[d].user_id);
                        struggling_student_list.splice(index, 1);
                    }
                });

                //push to success student list
                angular.forEach(completed_student_list, function(student) {
                    if (student_hint_history[student] && success_student_list.indexOf(student) == -1)
                        success_student_list.push(student);
                    var index = trying_student_list.indexOf(student);
                    if (index != -1)
                        trying_student_list.splice(index,1);
                });

                console.log(student_hint_history);
                $scope.attempting_student_list = attempting_student_list;
                $scope.struggling_student_list = struggling_student_list;
                $scope.trying_student_list = trying_student_list;
                $scope.success_student_list = success_student_list;
            });
        });
    }

    generate_hint_table();
    $interval(function(){generate_hint_table();}, 10000);

    $scope.editorOptions = {
        lineWrapping : true,
        lineNumbers: true,
        mode: 'python',
	    styleActiveLine: true,
	    matchBrackets: true
    };

    $scope.filter_function = {
        code: "def answer_filter(answer_string, parse_tree, eval_tree, correct_string, correct_tree, correct_eval, user_vars):\n  print answer_string\n  return True",
        author: Session.user_id,
        course: course
    };

    $scope.run_filter = function(){
        WebworkService.filterAnswers(course, set_id, problem_id, part_id,
                                     $scope.filter_function.code).
            success(function(response){
                console.log(response);
                $scope.filtered_list = response.matches;
                $scope.filter_output = response.output;
            }).error(function(error){
                console.error(error);
            });
    };

    $scope.toggle_filter_function = function(event){
        $scope.showFilterFunction = ! $scope.showFilterFunction;
    };

    $scope.toggle_groups = function(event){
        $scope.showGroups = ! $scope.showGroups;
    };

    var loadfilters = function(){
        HintsService.getFilterFunctions().success(function(funcs){
            $scope.filter_functions = funcs;
        });
    };
    loadfilters();

    $scope.save_filter = function(event){
        var ff = $scope.filter_function;
        console.log(ff);
        if(!ff.id){
            HintsService.createFilterFunction(
                ff.name, ff.course, ff.author, ff.code,
                ff.set_id, ff.problem_id).success(function(){
                    loadfilters();
                });

        }else{
            console.log(ff.id);
            HintsService.updateFilterFunction(
                ff.id, ff.code).success(function(){
                    loadfilters();
                });
        }
    };

    $scope.load_filter = function(){
        HintsService.getFilterFunctions({name: $scope.filter_function.name}).
            success(function(data){
                $scope.filter_function = data[0];
            });
    };
});
