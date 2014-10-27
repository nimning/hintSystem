angular.module('ta-console.directives')
  .directive('pgFilePreview', function($window, $sce, $compile, WebworkService) {
      return {
          restrict: 'EA',
          scope: {
              pgFile: '=',
              seed: '=',
              studentData: '=?',
              sockAnswers: '=?',
              box: '=?',
              showHintButtons: '@',
              psvn: '=?'
          },
          controller: function($scope){
              $scope.choose_box = function(boxname, b){
                  if($scope.box !== boxname){
                      $scope.box = boxname;
                  }else{
                      $scope.box = "";
                  }
              };

              $scope.box_class = function(boxname){
                  if($scope.box === boxname){
                      return 'btn-success';
                  }
                  return '';
              };
          },
          link: function($scope, element, attrs){
              $scope.hidePreview="";
              var renderPreview = function(){
                  console.info("someone asked us to re-render");
                  if($scope.pgFile && $scope.pgFile.length > 0 && $scope.seed!=undefined){
                      WebworkService.render($scope.pgFile, $scope.seed, $scope.psvn)
                          .success(function(data){
                              // Insert ng-model directive and disable the input
                              var s = data.rendered_html.replace(/name=('|")(AnSwEr\d+)('|")/g, "$& ng-model='$2.answer_string' disabled='' ng-class='{correct: $2.is_correct, incorrect: $2.is_correct===false}'");
                              s = '<div class="pg-file-rendered">'+$.trim(s)+'</div>';
                              var e = $compile(s)($scope);
                              element.children().remove();
                              element.append(e);
                              if ($scope.showHintButtons !== "false" &&
                                  $(element).find('button').length === 0){
                                  $(element).find('input[name^=AnSwEr]').each(function(i,el){
                                      var boxname = $(el).attr('name');
	                                  var button = $compile('<button class="btn add-hint-btn" ng-class="box_class(\''+boxname+'\')" ng-click="choose_box(\''+boxname+'\')"><span class="glyphicon glyphicon-plus"></span></button>')($scope);
                                      var part_indicator = $compile('<span class="badge">'+(i+1)+'</span>')($scope);
                                      $(el).after(part_indicator);
                                      $(el).after(button);

                                  });

                              }
                              if($scope.studentData && $scope.studentData.hints){
                                  for(var k = 0; k<$scope.studentData.hints.length; k++){
                                      var h = $scope.studentData.hints[k];
                                      var newEl = $($scope.insert_hint(h.hint_html,
			                                                           h.location,
			                                                           h.hintbox_id));
                                      var input_el = $(element).find("#"+h.location);
                                      $(input_el).before(newEl);
                                  }
                              }
                              $scope.hidePreview="hidden";
                          })
                          .error(function(){
                              console.log('Render returned an error');
                          });
                  }
              };
              $scope.$watch('pgFile', renderPreview);
              $scope.$watch('seed', renderPreview);
              $scope.$watch('psvn', renderPreview);
              // Note: If you append to this array, need to use $watchCollection insead of $watch
              $scope.$watch('studentData.answers', function(answers, oldAnswers, scope){
                  if(!!answers){
                      for(var i=0; i< answers.length; i++){
                          var ans = answers[i];
                          scope[ans.boxname] = ans;
                      }
                  }
              });

              // Insert a hint to a given location.
              $scope.insert_hint = function(hint_html, location, hintbox_id) {
                  hint_html = '<div style="float:right;">' +
	                  '<button onclick=remove_hint("'+ hintbox_id +
	                  '","' + location + '")>X</button></div>' + hint_html;
                  var d = document.createElement('div');
                  d.setAttribute('id', 'wrapper_' + hintbox_id);
                  d.innerHTML = hint_html;
                  d.setAttribute('style',
		                         'background-color: #E0FAC0; ' +
		                         'clear:left; ' +
		                         'margin:10px; ' +
		                         'border:1px solid; ' +
		                         'padding:5px; ');
                  return(d);
              };

              $scope.$watch('studentData.hints', function(hints, oldHints, scope){
                  if(hints){
                      // TODO: Move hint rendering into angularized code
                      renderPreview();
                  }
              });
          },
          templateUrl: 'partials/directives/pgFilePreview.html'
      };
  })
;
