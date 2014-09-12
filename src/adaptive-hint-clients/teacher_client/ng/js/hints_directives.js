angular.module('ta-console.directives')
    .directive('hintTable', function($window, WebworkService, SockJSService) {
        return {
            restrict: 'EA',
            scope: {
                hints: '=',
                selectedBox: '='
            },
            controller: function($scope) {

                $scope.displayed_hints = [];
                $scope.hints = [];

                $scope.reload_hints = function(){
                    WebworkService.problemHints(course, set_id, problem_id).success(function(data){
                        $scope.hints = data;
                    });
                };

                $scope.reload_hints();
                $scope.rendered_hint="";
                $scope.box="";
                $scope.preview_hint = function(hint){
                    $scope.hint = hint;
                    WebworkService.previewHint(hint, $scope.problem_seed, true).
                        then(function(rendered_html){
                            $scope.hint_html_template = rendered_html;
                            $scope.rendered_hint = $sce.trustAsHtml(rendered_html);
                        }, function(error){
                            console.log(error);
                        });
                };

                $scope.send_hint = function(){
                    SockJSService.add_hint(
                        course, set_id, problem_id, user_id, $scope.box, $scope.hint.hint_id, $scope.hint_html_template);
                };
                $scope.cancel_hint = function(){
                    $scope.rendered_hint = "";
                };


                $scope.new_hint = function(){
                    $scope.edited_hint = {
                        pg_header: $scope.pg_header,
                        pg_footer: $scope.pg_footer,
                        author: 'teacher',
                        set_id: set_id,
                        problem_id: problem_id
                    };
                };

                $scope.edit_hint = function(hint){
                    $scope.edited_hint = hint;
                };

                $scope.delete_hint = function(hint){
                    WebworkService.deleteHint(course, hint.hint_id).success($scope.reload_hints);
                };

            },
            link: function($scope, element, attrs) {
            }
        };
    });

angular.module('ta-console.directives')
    .directive('hintEditor', function($window, $timeout, $sce, WebworkService) {
        return {
            restrict: 'EA',
            scope: {
                hint: '=',
                pgFile: '=',
                seed: '=',
                course: '='
            },
            controller: function($scope) {
                $scope.editorOptions = {
                    lineWrapping : true,
                    lineNumbers: true,
                    mode: 'markdown',
	                styleActiveLine: true,
	                matchBrackets: true
                };

                $scope.pgFileEditorOptions = {
                    lineWrapping : true,
                    lineNumbers: true,
                    mode: 'perl',
	                styleActiveLine: true,
	                matchBrackets: true,
                    readOnly: true
                };

                $scope.cancel_edit_hint = function(){
                    $scope.hint=false;
                };

                $scope.save_hint = function(hint){
                    if(hint.hint_id){ // Hint is already in DB
                        WebworkService.updateHint($scope.course, hint.hint_id, hint.pg_text).
                            success(function(data){
                                $scope.hint=false;
                            });
                    }else{
                        WebworkService.createHint($scope.course, hint.set_id, hint.problem_id, 'teacher', hint.pg_text).
                            success(function(data){
                                $scope.hint=false;
                            });
                    }
                };

            },
            link: function($scope, element, attrs) {
                // Periodically preview hint so as to avoid jitter
                var previewHintTimer;
                $scope.$watch('hint.pg_text', function(newVal, oldVal){
                    if ($scope.hint) {
                        if(previewHintTimer){
                            $timeout.cancel(previewHintTimer);
                        }
                        previewHintTimer = $timeout(function(){
                            WebworkService.previewHint($scope.hint, $scope.seed, false).
                                then(function(rendered_html){
                                    $scope.hint_editor_preview = $sce.trustAsHtml(rendered_html);
                                });
                        }, 500);
                    }
                });
            },
            templateUrl: 'partials/directives/hint_editor.html'
        };
    });
