var App = angular.module('ta-console');

App.controller('ProblemPartCtrl', function($scope, $location, $window, $stateParams,
                                           $sce, $timeout, $interval, $anchorScroll, $modal, $log,
                                           WebworkService, SockJSService, APIHost,
                                           DTOptionsBuilder, DTColumnDefBuilder){

    var course = $scope.course = $stateParams.course;
    var set_id = $scope.set_id = $stateParams.set_id;
    var problem_id = $scope.problem_id = $stateParams.problem_id;
    var part_id = $scope.part_id = $stateParams.part_id;
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
        console.log(data);
        $scope.grouped_answers = data.correct;
        $scope.shown_answers_array = [];
        angular.forEach($scope.grouped_answers, function(value,group){sort_answers(value,group);});
        $scope.correct_terms = data.correct_terms;
    }).error(function(data){
        console.error(data);
    });

    function sort_answers(value, group){
        var answer_object = {};
        answer_object["signature"] = group;
        answer_object["student_list"] = value;
        var sum = 0;
        for (v in value){
            sum = sum + value[v].length;
        }
        answer_object["sum"] = sum
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

    /*$scope.groups_students_sum = [];
    $scope.sum = function(all_groups){
        for(value in all_groups){
            var s = 0;
            for (g in all_group[value]){
                s = s + group[g].length;
            }
            $scope.groups_students_sum.push(s);
        }
    };

    $scope.rearrange_groups = function(all_groups){
        return false;
    };*/

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

    var sock = SockJSService.get_sock();
    sock.onmessage = function(event) {
        print("RECEIVED: " + event.data);
        var data = JSON.parse(event.data);
        if (data.type === "my_students"){
            //$scope.my_students = data.arguments;
        }else if (data.type === "unassigned_students"){
            $scope.unassigned_students = data.arguments.filter(function(student){
                return student.problem_id == problem_id;
            });
        }
    };

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
        var hint_html_template = "";
        var rendered_hint="";
        // FIXME Put in the proper seed for the student
        // FIXME This should go inside the loop
        HintsService.previewHint($scope.hint, 1234, true).
            then(function(rendered_html){
                hint_html_template = rendered_html;
                rendered_hint = $sce.trustAsHtml(rendered_html);
            }, function(error){
                console.log(error);
            });

        for(var entry in group){ // For each different expression in the group
            for (var i=0; i<group[entry].length; i++){ //For each student
                var user_id = group[entry][i];
                SockJSService.request_student(course, set_id, problem_id, user_id);
                $timeout(function(){
                    SockJSService.add_hint(course, set_id, problem_id, user_id,
                                           "AnSwEr"+("0000"+part_id).slice(-4), id, hint_html_template);

                }, 1000);
            }
        }
    };

    $scope.validID = function(){
        if ($scope.hint_id == -1)
            return false;
        else
            return true;
    };

    $scope.test = function(){
        for (g in $scope.shown_answers_array){
            return g.sum;
        }
    };

    WebworkService.problemPartStatus(course, set_id, problem_id, part_id).success(function(data){
        $scope.completion_data = data;
    });

});
