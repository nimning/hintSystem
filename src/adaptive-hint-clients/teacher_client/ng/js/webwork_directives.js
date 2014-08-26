angular.module('ta-console.directives')
  .directive('pgFilePreview', function($window, $sce, $compile, WebworkService) {
      return {
          restrict: 'EA',
          scope: {
              pgFile: '=',
              seed: '=',
              studentData: '=',
              sockAnswers: '='
          },
          controller: function($scope){
          },
          link: function($scope, element, attrs){
              $scope.hidePreview="";
              $scope.$watch('pgFile', function(pgFile){
                  if($scope.pgFile && $scope.pgFile.length > 0){
                      WebworkService.render($scope.pgFile, String($scope.seed))
                          .success(function(data){
                              // Insert ng-model directive and disable the input
                              var s = data.rendered_html.replace(/name=('|")(AnSwEr\d+)('|")/g, "$& ng-model='$2' disabled=''");
                              s = '<div>'+$.trim(s)+'</div>';
                              var e = $compile(s)($scope);
                              element.append(e);
                              // $scope.pgFileRendered = $sce.trustAsHtml(s);
                              $scope.hidePreview="hidden";
                          })
                          .error(function(){
                              console.log('boo');
                          });
                  }
              });

              $scope.$watch('studentData.answers', function(answers, oldAnswers, scope){
                  if(!!answers){
                      var inputs = element.find('input[type=text]');
                      for(var i=0; i< answers.length; i++){
                          var $el=$(inputs[i]);
                          $el.val(answers[i]);
                          if(scope.studentData.scores[i]==="1"){
                              $el.removeClass('incorrect');
                              $el.addClass('correct');
                          }else{
                              $el.removeClass('correct');
                              $el.addClass('incorrect');
                          }
                      }

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
