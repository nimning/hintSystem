var App = angular.module('ta-console');

App.controller('ProblemUserCtrl', function($scope, $location, $window, $stateParams,
                                           $sce, $interval, $timeout, Session,
                                           WebworkService, SockJSService, HintsService, APIHost){
    var course = $scope.course = $stateParams.course;
    var set_id = $scope.set_id = $stateParams.set_id;
    var problem_id = $scope.problem_id = $stateParams.problem_id;
    var user_id = $scope.user_id = $stateParams.user_id;
    $scope.studentData = {answers: []};
    $scope.current_part = 1;
    $scope.problem_seed = "";
    $scope.psvn = "";
    $scope.hints = [];
    $scope.box="";
    $scope.displayed_answers = [];
    var user_id_for_problem_render = "pg_render";
    var password_for_problem_render = "pgrender";
    $scope.user_webwork_url = 'http://'+APIHost+'/webwork2/'+course+'/'+set_id+
        '/'+problem_id+'/?user='+user_id_for_problem_render+'&passwd='+password_for_problem_render+'&effectiveUser='+user_id;
    WebworkService.answersByPart(course, set_id, problem_id, user_id).
        success(function(data){
            $scope.answersByPart = {};
            angular.forEach(data, function(value){
                if (!$scope.answersByPart[value.part_id]){
                    $scope.answersByPart[value.part_id] = [];
                }
                $scope.answersByPart[value.part_id].push(value);
            });
            var answers = [];
            for(var part_id in $scope.answersByPart){
                var attempts = $scope.answersByPart[part_id].length;
                if(attempts > 0){
                    var answer = $scope.answersByPart[part_id][attempts - 1];
                    answer.is_correct = (parseInt(answer.score) === 1);
                    answer.boxname = WebworkService.partIdToBoxName(part_id);
                    answers.push( answer );
                }
            }
            $scope.studentData.answers = answers;
    });

    SockJSService.onMessage(function(event, data){
        if (data.type == 'student_info') {
	        var student_info = data['arguments'];
            $scope.$apply(function(){
                $scope.studentData = student_info;
            });
	    }
    });

    SockJSService.onConnect().then(function(){
        SockJSService.teacher_join(Session.user_id, $scope.course, $scope.set_id, $scope.problem_id, $scope.user_id);
        SockJSService.request_student($scope.course, $scope.set_id, $scope.problem_id, $scope.user_id);
        SockJSService.get_student_info($scope.course, $scope.set_id, $scope.problem_id, $scope.user_id);
    });
    // FIXME: There's a weird race condition when the seed and pg file are retrieved at the same time
    WebworkService.problemSeed(course, set_id, problem_id, user_id).
        success(function(data){
            $scope.problem_seed = data;
        });
    WebworkService.setPsvn(course, set_id, user_id).success(function(data){
        $scope.psvn = data;
    });
    WebworkService.problemPGFile(course, set_id, problem_id).success(function(data){
        $scope.pg_text = JSON.parse(data);
        var hf = WebworkService.extractHeaderFooter($scope.pg_text);
        $scope.pg_header = hf.pg_header;
        $scope.pg_footer = hf.pg_footer;
    });

    WebworkService.problemPGPath(course, set_id, problem_id).success(function(data){
        $scope.pg_path = JSON.parse(data);
    });

    // Auto send 'release_student' when closing window
    $scope.$on('$destroy', function(event){
        SockJSService.release_student(course, set_id, problem_id, user_id);
    });

    window.onbeforeunload = function() {
        SockJSService.release_student(course, set_id, problem_id, user_id);
    };

    $scope.showPart = function(part){
        $scope.current_part = part;
    };

    /**
     * Wait for the iFrame to get loaded and then extract the problem rendered in webwork and copy it here
     */
    $scope.checkIfIFrameLoaded = function() {
        var iFrame = $("#iFrameToRenderProblem")[0];
        if (iFrame && iFrame.contentDocument.readyState == "complete") {
            if (iFrame.contentWindow.document.getElementsByClassName("PGML")[0]) {
                if ($(".PGML")[0]) {
                    $(".PGML")[0].innerHTML = iFrame.contentWindow.document.getElementsByClassName("PGML")[0].innerHTML;
                    return;
                } else if ($("#problem-content")[0]) {
                    $("#problem-content")[0].innerHTML = iFrame.contentWindow.document.getElementsByClassName("PGML")[0].innerHTML;
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
