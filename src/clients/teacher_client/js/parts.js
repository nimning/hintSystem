var App = angular.module('ta-console');

App.controller('PartsCtrl', function($scope, $location, $window, $stateParams, $interval,
                                      WebworkService, SockJSService,
                                      DTOptionsBuilder, DTColumnDefBuilder, CurrentCourse){
    var course = $scope.course = $stateParams.course;
    CurrentCourse.name = $scope.course;
    WebworkService.answersByPartCounts(course).success(function(data){
        $scope.answers_by_part = data;
    });

    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withOption('paging', false);

    $scope.dtColumnDefs = [
        DTColumnDefBuilder.newColumnDef(0),
        DTColumnDefBuilder.newColumnDef(1),
        DTColumnDefBuilder.newColumnDef(2),
        DTColumnDefBuilder.newColumnDef(2)
    ];

    $scope.$on('event:dataTableLoaded', function(event, loadedDT) {
        loadedDT.dataTable.rowGrouping({
            iGroupingColumnIndex:0,
            sGroupingColumnSortDirection: "asc",
            bExpandableGrouping: true,
            asExpandedGroups: [],
        });
        loadedDT.DataTable.search("week").draw();
        $('.customAjaxLoaderScreen').removeClass("visible");
    });

});
