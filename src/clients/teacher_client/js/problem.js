var App = angular.module('ta-console');

App.controller('ProblemCtrl', function($scope, $location, $window, $stateParams, $sce, $timeout, $interval, $anchorScroll,
                                       WebworkService, HintsService, SockJSService, APIHost,
                                       DTOptionsBuilder, DTColumnDefBuilder, Session, user_id_for_problem_render, password_for_problem_render){
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
    $scope.attempting_student_list = {};
    $scope.completed_student_list = {};
    var user_id = $scope.user_id = Session.user_id;
    
    $scope.user_webwork_url = 'http://'+APIHost+'/webwork2/'+course+'/'+set_id+
        '/'+problem_id+'/?user='+user_id_for_problem_render+'&passwd='+password_for_problem_render+'&effectiveUser='+user_id;

    $scope.scrollTo = function($event) {
        $event.preventDefault();
        var id = $($event.target).attr('href').substr(1);
        var old = $location.hash();
        $location.hash(id);
        $anchorScroll();
        //reset to old to keep any additional routing logic from kicking in
        $location.hash(old);
    };

    WebworkService.answersByPart(course, set_id, problem_id).success(function(data){
        var attempting_student_list = {};
        var completed_student_list = {};
        var answers_data = $scope.answers_data = data;
        //push students who are attempting to the list
        for (s in answers_data) {
            var local_part_id = answers_data[s].part_id;
            var local_user_id = answers_data[s].user_id;

            if (!attempting_student_list[local_part_id]) //init
                attempting_student_list[local_part_id] = [];
            if (!completed_student_list[local_part_id]) //init
                completed_student_list[local_part_id] = [];

            if (answers_data[s].score == 0) {
                if (attempting_student_list[local_part_id].indexOf(local_user_id) == -1)
                    attempting_student_list[local_part_id].push(local_user_id);
            }
        }
        //push students who are done to complete list and remove from struggle list
        for (s in answers_data) {
            var local_part_id = answers_data[s].part_id;
            var local_user_id = answers_data[s].user_id;
            if (answers_data[s].score == 1) {
                var index = (attempting_student_list[local_part_id]).indexOf(local_user_id);
                if (index != -1){
                    (attempting_student_list[local_part_id]).splice(index, 1);
                }
                index = completed_student_list[local_part_id].indexOf(local_user_id);
                if (index === -1)
                    completed_student_list[local_part_id].push(local_user_id);
            }
        }

        $scope.attempting_student_list = attempting_student_list;
        $scope.completed_student_list = completed_student_list;
    });



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
        for(i=1; i<=part_count; i++){
            $scope.attemptsByPart[i].attempting = $scope.attempting_student_list[i].length;
            $scope.attemptsByPart[i].completed = $scope.completed_student_list[i].length;
        }

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

        for (i in $scope.attemptsByPart) //init
                $scope.attemptsByPart[i].hint_history = 0;

        HintsService.assignedHintHistoryOfProblem(course, set_id, problem_id).success(function(data) {
            for (i in $scope.attemptsByPart) {
                for (d in data) {
                    if (data[d].pg_id === "AnSwEr"+("0000"+i).slice(-4))
                        $scope.attemptsByPart[i].hint_history++;
                }
            }
        });
    }); // End exportProblemData promise resolver


    SockJSService.onMessage(function(event, data) {
        if (data.type === "my_students"){
            $scope.my_students = data.arguments;
        }else if (data.type === "unassigned_students"){
            $scope.unassigned_students = data.arguments.filter(function(student){
                return student.problem_id == problem_id;
            });
        }
    });


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

    /**
     * Wait for the iFrame to get loaded and then extract the problem rendered in webwork and copy it here
     */
    $scope.checkIfIFrameLoaded = function() {
        var iFrame = $("#iFrameToRenderProblem")[0];
        if (iFrame && iFrame.contentDocument.readyState == "complete") {
            if (iFrame.contentWindow.document.getElementsByClassName("problem-content")[0]) {
                if ($(".PGML")[0]) {
                    $(".PGML")[0].innerHTML = iFrame.contentWindow.document.getElementsByClassName("problem-content")[0].innerHTML;
                    return;
                } else if ($("#problem-content")[0]) {
                    $("#problem-content")[0].innerHTML = iFrame.contentWindow.document.getElementsByClassName("problem-content")[0].innerHTML;
                    return;
                }
            } else if (iFrame.contentWindow.document.getElementById("problem-content")) {
                $("#problem-content")[0].innerHTML = iFrame.contentWindow.document.getElementById("problem-content").innerHTML;
                return;
            }
        }
        window.setTimeout(function() {
            $scope.checkIfIFrameLoaded();
        }, 250);
    }

    /**
     * Open the problem from the webwork server from student POV. This enables to render the problem as its displayed for each student.
     */
    $scope.openProblemPageInIFrame = function() {
        if ($("#iFrameToRenderProblem").length) {
            $("#iFrameToRenderProblem")[0].parentNode.removeChild($("#iFrameToRenderProblem")[0]);
        }
        $("<iframe id='iFrameToRenderProblem' name='problemRender'>").appendTo("body");
        $("#iFrameToRenderProblem").css("display", "none");

        var srcUrl = $scope.user_webwork_url;
        $("#iFrameToRenderProblem").attr("src", srcUrl);
        $scope.checkIfIFrameLoaded();
    }

    window.setTimeout(function() {
        $scope.openProblemPageInIFrame();
    }, 250);
});
