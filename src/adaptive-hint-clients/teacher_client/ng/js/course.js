var App = angular.module('ta-console');

App.controller('CourseCtrl', function($scope, $location, $window, $routeParams,
                                      WebworkService, DTOptionsBuilder, DTColumnDefBuilder, CurrentCourse){
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

App.controller('SetCtrl', function($scope, $location, $window, $routeParams,
                                   WebworkService, DTOptionsBuilder, DTColumnDefBuilder){
    $scope.course = $routeParams.course;
    $scope.set_id = $routeParams.set_id;
    WebworkService.problems($scope.course, $scope.set_id, function(data){
        $scope.problems = data;
        console.log(data);
    });

    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withBootstrap();

    $scope.dtColumnDefs = [
        DTColumnDefBuilder.newColumnDef(0),
        DTColumnDefBuilder.newColumnDef(1),
        DTColumnDefBuilder.newColumnDef(2)
    ];
});

App.controller('ProblemCtrl', function($scope, $location, $window, $routeParams, $sce,
                                       WebworkService, DTOptionsBuilder, DTColumnDefBuilder){
    $scope.course = $routeParams.course;
    $scope.set_id = $routeParams.set_id;
    $scope.problem_id = $routeParams.problem_id;
    $scope.attempts = {};
    $scope.problem_data = {};
    $scope.studentData = {answers: []};

    WebworkService.exportProblemData($scope.course, $scope.set_id, $scope.problem_id).success(function(data){
        $scope.problem_data = data;
        pg_text = data.pg_file;
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

        for(var i=0; i<data.hints.length; i++){
            hint_text = pg_header + '\n' + $scope.problem_data.hints[i].pg_text +
                '\n' + pg_footer;
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
        var attemptsByPart = [];
        
        for(i=0; i<data.past_answers[0].scores.length; i++){
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
                            attemptsByPart[j]++;
                        }
                        if(past_answer.scores[j]=="1"){
                            scores[j]=true;
                        }
                    }
                }
            });
        });

        console.log(attemptsByPart);

    });


    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withBootstrap();

    $scope.dtColumnDefs = [
        DTColumnDefBuilder.newColumnDef(0),
        DTColumnDefBuilder.newColumnDef(1),
        DTColumnDefBuilder.newColumnDef(2)
    ];

});
