angular.module('ta-console.directives')
    .directive('hintTable', function($window, $sce, WebworkService,
                                     SockJSService, Session) {
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
                        author: Session.user_id,
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
    .directive('hintEditor', function($window, $timeout, $sce, WebworkService,
                                     HintFilterProperties, HintsService) {
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

                $scope.hint_filter_options={};
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
                        WebworkService.createHint($scope.course, hint.set_id,
                                                  hint.problem_id, hint.author, hint.pg_text).
                            success(function(new_hint_id){
                                $scope.hint=false;
                                if($scope.hint_filter){ // A Hint Filter was selected
                                    HintsService.createHintFilter(
                                        $scope.course, parseInt(new_hint_id), $scope.hint_filter.id,
                                        $scope.hint_filter_options.trigger_condition);
                                }

                            });
                    }

                    if($scope.hint_filter){ // A Hint Filter was selected
                        if($scope.hint_filter_options.update){
                            HintsService.updateHintFilter(
                                $scope.course, hint.hint_id, $scope.hint_filter.id,
                                $scope.hint_filter_options.trigger_condition);
                        }else{
                            HintsService.createHintFilter(
                                $scope.course, hint.hint_id, $scope.hint_filter.id,
                                $scope.hint_filter_options.trigger_condition);

                        }
                    }
                };

                $scope.check_answers = function(hint){
                    var hint_text = hint.pg_header + '\n' + hint.pg_text + '\n' + hint.pg_footer;
                    var $el = $("#HINTBOXID");
                    var answer_val = $el.val();
                    $scope.checking_hint = true;
                    WebworkService.checkAnswer(hint_text, $scope.seed, {AnSwEr0001: answer_val}).
                        success(function(data){
                            $scope.checking_hint = false;
                            if (data.AnSwEr0001.is_correct){
                                $el.removeClass('incorrect');
                                $el.addClass('correct');
                            }else{
                                $el.removeClass('correct');
                                $el.addClass('incorrect');
                            }
                        }).error(function(data){
                        });
                };

            },
            link: function($scope, element, attrs) {
                WebworkService.hintFilters($scope.course).success(function(filters){
                    $scope.hint_filters = filters.map(function(filter){
                        return angular.extend(filter, HintFilterProperties[filter.filter_name]);
                    });
                });
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
                // Workaround for bug with ng-show. There's supposed to be a
                // ui-refresh option which handles this but it doesn't work.
                $scope.$watch('hint', function(newVal, oldVal){
                    if(newVal && !oldVal){ // A new hint has been loaded
                        $(".CodeMirror").each(function(i, el){
                            el.CodeMirror.refresh();
                        });
                        if(typeof newVal.hint_id !== 'undefined'){ // Editing existing hint
                            HintsService.getHintFilter($scope.course, newVal.hint_id).
                                success(function(data){
                                    if(data.length > 0){
                                        $scope.hint_filter_options.trigger_condition=data[0].trigger_cond;
                                        $scope.hint_filter_options.update = true;

                                        angular.forEach($scope.hint_filters, function(hf){
                                            if(hf.id == data[0].filter_id){
                                                $scope.hint_filter = hf;
                                            }
                                        });
                                    }else{ // No hint filter previously assigned
                                        $scope.hint_filter=undefined;
                                        $scope.hint_filter_options={};
                                    }
                                });
                        }else{ // No hint filter since this is a new hint
                            $scope.hint_filter=undefined;
                            $scope.hint_filter_options={};
                        }

                    }
                });
            },
            templateUrl: 'partials/directives/hint_editor.html'
        };
    });
