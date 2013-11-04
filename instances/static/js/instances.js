(function(window){

    function url_for(name, formatting) {
        var URLS = {
            "user_info": $("body").data("user-info-url"),
            "repositories": $("body").data("repo-list-url"),
            "tracking_code_modal": $("body").data("tracking-code-modal-url")
        };
        var url = URLS[name];
        for (var key in formatting) {
            var pattern = encodeURIComponent('<' + key + '>');
            var replacement = formatting[key]
            url = url.replace(pattern, replacement);
        }
        return url;
    };
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
        $scope.ORGANIZATIONS = {};
        $scope.current_project = null;

        $scope.ShowTrackingCode = function(organization, project){
            $.getJSON(url_for('tracking_code_modal', {"owner": organization.login, "name": project.name}), function(data){
                $scope.$apply(function(){
                    $("body .modal").remove();
                    $("body").append(data.modal_html);
                });
            });
        };

        $scope.ChooseOrganization = function(organization){
            $scope.current_organization = organization;
            if ($scope.ORGANIZATIONS[organization.login]) {
                return;
            }
            $.getJSON(url_for('repositories', {"owner": organization.login}), function(data){
                $scope.$apply(function(){
                    $scope.ORGANIZATIONS[organization.login] = data;
                    $scope.current_organization = data.organization;
                });
            });
        };

    });

    $(function(){
        var $scope = angular.element($("body")).scope();
        $.getJSON(url_for('user_info'), function(data) {
            $scope.$apply(function(){
                $scope.user_info = data;
                $scope.ORGANIZATIONS[data.organization.login] = data;
                $scope.current_organization = data.organization;
            });
        });
    });
})(window);