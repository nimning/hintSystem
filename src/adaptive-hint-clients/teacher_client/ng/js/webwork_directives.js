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
                  if($scope.pgFile && $scope.pgFile.length > 0 && $scope.seed!=undefined){
                      WebworkService.render($scope.pgFile, $scope.seed, $scope.psvn)
                          .success(function(data){
                              // Insert ng-model directive and disable the input
                              var s = data.rendered_html.replace(/name=('|")(AnSwEr\d+)('|")/g, "$& ng-model='$2' disabled=''");
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
              // $scope.$watch('studentData.answers', function(answers, oldAnswers, scope){
              //     if(!!answers){
              //         var inputs = element.find('input[type=text]');
              //         for(var i=0; i< answers.length; i++){
              //             var $el=$(inputs[i]);
              //             $el.val(answers[i]);
              //             if(answers[i].correct === 1){
              //                 $el.removeClass('incorrect');
              //                 $el.addClass('correct');
              //             }else{
              //                 $el.removeClass('correct');
              //                 $el.addClass('incorrect');
              //             }
              //         }

              //     }
              // });

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
                      console.log(hints);
                      renderPreview();
                  }
              });

              $scope.$watch('sockAnswers', function(answers, oldAnswers, scope){
                  if(!!answers){
                      for(var i=0; i< answers.length; i++){
                          var ans = answers[i];
                          scope[ans.boxname] = ans.answer_string;
                          var $el=$('input[name='+ans.boxname+']');
                          // $el.val(ans.answer_string);
                          // Should probably do this in a more 'Angular' way, but meh
                          if(ans.correct===1){
                              $el.removeClass('incorrect');
                              $el.addClass('correct');
                          }else{
                              $el.removeClass('correct');
                              $el.addClass('incorrect');
                          }
                      }
                  }
              });

          },
          templateUrl: 'partials/directives/pgFilePreview.html'
      };
  })
;
