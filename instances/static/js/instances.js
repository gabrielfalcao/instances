(function(window){
    window.INSTANCES = angular.module('instances', []).
        filter('dashify', function() {
            return function(input) {
                return input.replace("/", "-");
            }
        }).
        filter('length', function() {
            return function(input) {
                return input.length;
            }
        });;

    window.INSTANCES.controller("InstancesController", function($scope){
        $scope.user_info = null;
        $scope.ShowTrackingCode = function(project){
            alert(project.full_name);
        };
    });

    $(function(){
        var URLS = {
            "user_info": $("body").data("user-info-url")
        };
        var scope = angular.element($("body")).scope();
        $.getJSON(URLS.user_info, function(data) {
            scope.$apply(function(){
                scope.user_info = data;
            });
        });
    });

})(window);