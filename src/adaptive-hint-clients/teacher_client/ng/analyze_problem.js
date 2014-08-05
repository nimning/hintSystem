var App = angular.module('ta-console');

App.controller('AnalyzeProblemCtrl', function($scope, $location, $window, $routeParams, $http, $sce, PGService){
    $scope.problem_data = {};
    $scope.attempts = {};
    $scope.problem_data.pg_file = "PG Text here";
    $scope.readFile = function(){
        var selected_file = $('#json_file').get(0).files[0];
        console.log(selected_file);

        var reader = new FileReader();

        // Closure to capture $scope
        reader.onload = (function($scope) {
            return function(e) {
                $scope.$apply(function(){
                    data = JSON.parse(e.target.result);
                    $scope.problem_data = data;
                    PGService.render(data.pg_file, "1234", function(result){
                        $scope.rendered_problem = $sce.trustAsHtml(result.rendered_html);
                    });
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
                    var i=0;
                    for(i=0; i<data.hints.length; i++){
                        hint_text = pg_header + '\n' + $scope.problem_data.hints[i].pg_text +
                            '\n' + pg_footer;
                        PGService.render(hint_text, "1234", function(idx, result){
                                // $scope.$apply(function(){
                                $scope.problem_data.hints[idx].rendered_html = result.rendered_html;
                                // });
                        }.bind(this, i));
                    }

                    var start = performance.now();
                    console.log("Start collecting students");
                    for( attempt of data.past_answers){
                        if(!$scope.attempts[attempt.user_id]){
                            $scope.attempts[attempt.user_id] = [];
                        }
                        $scope.attempts[attempt.user_id].push(attempt);
                    }
                    var time = performance.now() - start;
                    console.log("Done collecting students in "+time+" ms");
                });
            };
        })($scope);

        // Read in the file
        reader.readAsText(selected_file);
    };
});
