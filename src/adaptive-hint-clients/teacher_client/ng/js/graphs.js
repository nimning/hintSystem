angular.module('ta-console.directives')
    .directive('studentTimeline', function($window) {
        return {
            restrict: 'EA',
            scope: {
                activity: '=',
                student: '=',
                studentData: '='
            },
            controller: function($scope) {
                $scope.click = function click(element){
                    var answers = element.answer_string.split('\t');
                    $scope.$apply(function(){
                        $scope.studentData.answers = answers;
                        $scope.studentData.scores = element.scores;
                    });
                };
            },
            link: function($scope, element, attrs) {
                var svg = d3.select(element[0])
                        .append("svg").style('width', '100%');
                // Browser onresize event
                $window.onresize = function() {
                    $scope.$apply();
                };

                // Watch for resize event
                $scope.$watch(function() {
                    return angular.element($window)[0].innerWidth;
                }, function() {
                    $scope.render($scope.activity);
                });

                countScore = function(scores){
                    var total = 0;
                    for(var i=0; i< scores.length; i++){
                        if(scores[i]=="1"){
                            total++;
                        }
                    }
                    return total/scores.length;
                };
                var margin = parseInt(attrs.margin) || 20,
                    barHeight = parseInt(attrs.barHeight) || 20,
                    barPadding = parseInt(attrs.barPadding) || 5,
                    radius=10,
                    border=2;
                $scope.render = function(data) {
                    // our custom d3 code
                    // svg.selectAll('*').remove();

                    // If we don't pass any data, return out of the element
                    if (!data) return;

                    // setup variables
                    var width = d3.select(element[0]).node().offsetWidth - margin,
                        height = 100,
                        // Use the category20() scale function for multicolor support
                        color = d3.scale.category20(),
                        spacing = (width-(radius+border)*2)/(data.length-1);

                    svg.attr('height', height);
                    svg.selectAll('rect.timeline')
                        .data([width]).enter()
                        .append('rect')
                        .attr('class', 'timeline')
                        .attr('x', radius+border)
                        .attr('y', height/2-2)
                        .attr('width', (radius+border))
                        .attr('height', 4)
                        .attr('fill', '#555555');

                    svg.selectAll('rect.timeline')
                        .data([width])
                        .transition()
                        .duration(1000)
                        .attr('width', width-2*(radius+border));

                    svg.selectAll('circle')
                        .data(data).enter()
                        .append('circle')
                        .attr('r', radius)
                        .attr('cy', Math.round(height/2))
                        .attr('cx', border+radius)
                        .attr('fill', function(d) { return color(countScore(d.scores)*20); })
                    ;

                    svg.selectAll('circle')
                        .data(data)
                        .transition()
                        .duration(1000)
                        .attr('cx', function(d,i) {
                            return i * (spacing)+radius+border;
                        })

                    ;
                    svg.selectAll('circle.border')
                        .data(data).enter()
                        .append('circle')
                        .attr('class', 'border')
                        .attr('r', 10)
                        .attr('cy', Math.round(height/2))
                        .attr('cx', border+radius)
                        .attr("fill", "rgba(1,1,1,0)")
                        .attr("stroke", "#000000")
                        .attr("stroke-width", "2px")
                    ;

                    svg.selectAll('circle.border')
                        .data(data)
                        .attr('class', 'border')
                        .transition()
                        .duration(1000)
                        .attr('cx', function(d,i) {
                            return i * (spacing) + radius + border;
                        })
                    ;

                    svg.selectAll('circle.border').on('click', $scope.click);

                };
            }};
    });
