var App = angular.module('ta-console');

App.controller('CourseCtrl', function($scope, $location, $window, $routeParams, $interval,
                                      WebworkService, SockJSService,
                                      DTOptionsBuilder, DTColumnDefBuilder, CurrentCourse){
    $scope.course = $routeParams.course;
    CurrentCourse.name = $scope.course;
    WebworkService.sets($scope.course, function(data){
        $scope.sets = data;
    });

    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withBootstrap();

    $scope.dtColumnDefs = [
        DTColumnDefBuilder.newColumnDef(0),
        DTColumnDefBuilder.newColumnDef(1),
        DTColumnDefBuilder.newColumnDef(2)
    ];

});

App.controller('SetCtrl', function($scope, $location, $window, $routeParams, $interval, $timeout,
                                   WebworkService, SockJSService, DTOptionsBuilder, DTColumnDefBuilder){
    $scope.course = $routeParams.course;
    $scope.set_id = $routeParams.set_id;
    WebworkService.problems($scope.course, $scope.set_id).success(function(data){
        $scope.problems = data;
        console.log(data);

    });

    $scope.unassigned_students = [];
    $scope.displayed_students = [];

    $scope.my_students = [];
    var sock = SockJSService.get_sock();
    sock.onmessage = function(event) {
        print("RECEIVED: " + event.data);
        var data = JSON.parse(event.data);
        if (data.type === "my_students"){
            $scope.my_students = data.arguments;
        }else if (data.type === "unassigned_students"){
            $scope.unassigned_students = data.arguments;
        }
    };

    // Angular Smart-table is weird about updating the first time
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
    ];

    $scope.$on('$destroy', function(event){
        $interval.cancel(list_students);
    });
});

App.controller('ProblemCtrl', function($scope, $location, $window, $routeParams, $sce,
                                       WebworkService, DTOptionsBuilder, DTColumnDefBuilder){
    $scope.course = $routeParams.course;
    $scope.set_id = $routeParams.set_id;
    $scope.problem_id = $routeParams.problem_id;
    $scope.attempts = {};
    $scope.problem_data = {};
    $scope.studentData = {answers: []};
    $scope.attemptsByPart={};
    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withDOM('rtip')
        .withBootstrap();
    $scope.dtOptions['dom'] = 'rtip';

    console.log($scope.dtOptions);
    WebworkService.exportProblemData($scope.course, $scope.set_id, $scope.problem_id).success(function(data){
        $scope.problem_data = data;
        var headerFooter = WebworkService.extractHeaderFooter(data.pg_file);

        for(var i=0; i<data.hints.length; i++){
            var hint_text = headerFooter.pg_header + '\n' + $scope.problem_data.hints[i].pg_text +
                '\n' + headerFooter.pg_footer;
            WebworkService.render(hint_text, "1234").success(function(idx, result){
                $scope.problem_data.hints[idx].rendered_html = result.rendered_html;
            }.bind(this, i))
            .error(function(){
                console.log('boo');
            });
        }

        data.past_answers.forEach( function(attempt){
            if(!$scope.attempts[attempt.user_id]){
                $scope.attempts[attempt.user_id] = [];
            }
            $scope.attempts[attempt.user_id].push(attempt);
        });
        var attemptsByPart = {};
        var part_count = data.pg_file.match(/\[_+\]/g).length;
        for(i=1; i<=part_count; i++){
            attemptsByPart[i]=0;
        }
        // Calculate number of attempts per part: A past answer counts
        // for a part if it was not previously answered correctly and
        // the answer for the part is nonempty
        angular.forEach($scope.attempts, function(value, user_id){
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
        });

        $scope.attemptsByPart = attemptsByPart;

    });


    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withBootstrap();

    $scope.dtColumnDefs = [
        DTColumnDefBuilder.newColumnDef(0),
        DTColumnDefBuilder.newColumnDef(1),
        DTColumnDefBuilder.newColumnDef(2)
    ];

});
