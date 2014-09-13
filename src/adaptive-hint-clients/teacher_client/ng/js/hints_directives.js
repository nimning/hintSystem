angular.module('ta-console.directives')
    .directive('hintTable', function($window, $sce, WebworkService, SockJSService) {
        return {
            restrict: 'EA',
            scope: {
                hints: '=',
                selectedBox: '=',
                course: '=',
                setId: '=',
                problemId: '=',
                userId: '=',
                seed: '=',
                editedHint: '=',
                pgHeader: '=',
                pgFooter: '=',
                enableSend: '=?'
            },
            controller: function($scope) {
                $scope.enableSend = angular.isDefined($scope.enableSend) ? $scope.enableSend : true;
                $scope.displayed_hints = [];

                $scope.reload_hints = function(){
                    WebworkService.problemHints($scope.course, $scope.setId, $scope.problemId).
                        success(function(data){
                            $scope.hints = data;
                        });
                };

                $scope.reload_hints();
                $scope.rendered_hint="";
                $scope.preview_hint = function(hint){
                    $scope.hint = hint;
                    WebworkService.previewHint(hint, $scope.seed, true).
                        then(function(rendered_html){
                            $scope.hint_html_template = rendered_html;
                            $scope.rendered_hint = $sce.trustAsHtml(rendered_html);
                        }, function(error){
                            console.log(error);
                        });
                };

                $scope.send_hint = function(){
                    SockJSService.add_hint(
                        $scope.course, $scope.setId, $scope.problemId, $scope.userId, $scope.selectedBox, $scope.hint.hint_id, $scope.hint_html_template);
                };
                $scope.cancel_hint = function(){
                    $scope.rendered_hint = "";
                };


                $scope.new_hint = function(){
                    $scope.editedHint = {
                        pg_header: $scope.pgHeader,
                        pg_footer: $scope.pgFooter,
                        author: 'teacher',
                        set_id: $scope.setId,
                        problem_id: $scope.problemId
                    };
                };

                $scope.edit_hint = function(hint){
                    $scope.editedHint = hint;
                };

                $scope.delete_hint = function(hint){
                    WebworkService.deleteHint($scope.course, hint.hint_id).success($scope.reload_hints);
                };
                $scope.$watch('editedHint', function(newVal, oldVal){
                    // When the edited hint is unset, some editing operation was finished
                    if(!newVal){
                        $scope.reload_hints();
                    }
                });


            },
            link: function($scope, element, attrs) {
            },
            templateUrl: 'partials/directives/hint_table.html'
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
