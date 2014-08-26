angular.module('ta-console.directives')
  .directive('pgFilePreview', function($window, $sce, WebworkService) {
      return {
          restrict: 'EA',
          scope: {
              pgFile: '=',
              seed: '=',
              studentData: '='
          },
          controller: function($scope){
          },
          link: function($scope, element, attrs){
              $scope.hidePreview="";
              $scope.$watch('pgFile', function(pgFile){
                  if($scope.pgFile && $scope.pgFile.length > 0){
                      WebworkService.render($scope.pgFile, String($scope.seed))
                          .success(function(data){
                              $scope.pgFileRendered = $sce.trustAsHtml(data.rendered_html);
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


          },
          templateUrl: 'partials/directives/pgFilePreview.html'
      };
  })
;
