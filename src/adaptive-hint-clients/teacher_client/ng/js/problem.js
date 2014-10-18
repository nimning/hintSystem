var App = angular.module('ta-console');

App.controller('ProblemCtrl', function($scope, $location, $window, $stateParams, $sce, $timeout, $interval, $anchorScroll,
                                       WebworkService, SockJSService, APIHost,
                                       DTOptionsBuilder, DTColumnDefBuilder){
    var course = $scope.course = $stateParams.course;
    var set_id = $scope.set_id = $stateParams.set_id;
    var problem_id = $scope.problem_id = $stateParams.problem_id;
    $scope.attempts = {};
    $scope.problem_data = {};
    $scope.studentData = {answers: []};
    $scope.attemptsByPart={};
    $scope.displayed_hints = [];
    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withDOM('rtip')
        .withBootstrap();
    $scope.dtOptions['dom'] = 'rtip';

    $scope.scrollTo = function($event) {
        $event.preventDefault();
        var id = $($event.target).attr('href').substr(1);
        var old = $location.hash();
        $location.hash(id);
        $anchorScroll();
        //reset to old to keep any additional routing logic from kicking in
        $location.hash(old);
    };

    $scope.download_json_url = 'http://'+APIHost+':4351/export_problem_data?course='+course+'&set_id='+set_id+'&problem_id='+problem_id;
    WebworkService.exportProblemData($scope.course, $scope.set_id, $scope.problem_id).success(function(data){
        $scope.problem_data = data;
        var headerFooter = WebworkService.extractHeaderFooter(data.pg_file);
        $scope.pg_header = headerFooter.pg_header;
        $scope.pg_footer = headerFooter.pg_footer;
        data.past_answers.forEach( function(attempt){
            if(!$scope.attempts[attempt.user_id]){
                $scope.attempts[attempt.user_id] = [];
            }
            $scope.attempts[attempt.user_id].push(attempt);
        });

        $scope.realtime_attempts = {};
        var realtime_attempts = {};
        data.realtime_past_answers.forEach( function(attempt){
            if(!realtime_attempts[attempt.user_id]){
                realtime_attempts[attempt.user_id] = [];
            }
            realtime_attempts[attempt.user_id].push(attempt);
        });
        $scope.realtime_attempts = realtime_attempts;
        var attemptsByPart = {};
        var part_count = data.pg_file.match(/\[_+\]/g).length;
        for(i=1; i<=part_count; i++){
            attemptsByPart[i]=0;
            $scope.attemptsByPart[i] = {};
        }

        $scope.historical_students = [];
        $scope.displayed_historical_students = [];
        angular.forEach($scope.attempts, function(value, user_id){
            // Calculate number of attempts per part: A past answer counts
            // for a part if it was not previously answered correctly and
            // the answer for the part is nonempty
            var scores = []; // Keep track of student's score per part
            angular.forEach(value, function(past_answer){
                var part_answers = past_answer.answer_string.split('\t');
                for(var j=0; j<part_answers.length; j++){
                    if(!scores[j]){ // Student has not yet answered correctly
                        if(part_answers[j].length>0){ // Answer is nonempty
                            attemptsByPart[j+1]++;
                        }
                        if(past_answer.scores[j]=="1"){
                            scores[j]=true;
                        }
                    }
                }
            });
            var last_answer;
            var realtime_tries;
            if(realtime_attempts[user_id]){
                realtime_tries = realtime_attempts[user_id].length;
                last_answer = realtime_attempts[user_id][realtime_tries-1];
            }else{
                realtime_tries = 0;
                last_answer = {};
            }
            var student_summary = {
                student_id: user_id,
                realtime_past_answers: realtime_attempts[user_id] || [],
                past_answers: $scope.attempts[user_id],
                total_tries: $scope.attempts[user_id].length,
                realtime_tries: realtime_tries,
                last_answer: last_answer,
                last_attempt_time: last_answer.timestamp,
                is_online: false
            };
            $scope.historical_students.push(student_summary);
        });
        angular.forEach(attemptsByPart, function(value, key){
            $scope.attemptsByPart[key].submitted = value;
        });

        // Gather hint statistics
        var hints = {};
        angular.forEach(data.hints, function(value){
            hints[value.id] = value;
            hints[value.id].assigned_hints = [];
            hints[value.id].feedback = [];
            hints[value.id].feedback_counts = {
                helpful: 0, 'easy but unhelpful': 0, 'too hard': 0
            };
        });
        var assigned_hints = {};
        angular.forEach(data.assigned_hints, function(value){
            hints[value.hint_id].assigned_hints.push(value);
            assigned_hints[value.id] = value;
        });
        angular.forEach(data.hint_feedback, function(value){
            var hint_id = assigned_hints[value.assigned_hint_id].hint_id;
            hints[hint_id].feedback.push(value);
            hints[hint_id].feedback_counts[value.feedback]++;
        });
        // $scope.hints = [];
        // angular.forEach(hints, function(value, key){
        //     $scope.hints.push(value);
        // });
    }); // End exportProblemData promise resolver

    var sock = SockJSService.get_sock();
    sock.onmessage = function(event) {
        print("RECEIVED: " + event.data);
        var data = JSON.parse(event.data);
        if (data.type === "my_students"){
            $scope.my_students = data.arguments;
        }else if (data.type === "unassigned_students"){
            $scope.unassigned_students = data.arguments.filter(function(student){
                return student.problem_id == problem_id;
            });
        }
    };


    WebworkService.problemStatus(course, set_id, problem_id).success(function(data){
        $scope.completion_data = data;
    });

    /* Angular Smart-table is weird about updating the first time*/
    $timeout(function(){
        SockJSService.send_command('list_students', {'set_id': $scope.set_id});
    }, 500);

    var list_students =$interval(function(){
        SockJSService.send_command('list_students', {'set_id': $scope.set_id});
    }, 1000);

    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withBootstrap();

    $scope.dtColumnDefs = [
        DTColumnDefBuilder.newColumnDef(0),
        DTColumnDefBuilder.newColumnDef(1),
        DTColumnDefBuilder.newColumnDef(2)
    ];/**/


});
