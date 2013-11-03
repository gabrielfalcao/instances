$(function(){
    var scope = angular.element($("#sidebar")).scope();

    scope.$apply(function(){
        scope.ShowForks = function(project){
            alert("FORKS")
        };
        scope.ShowStars = function(project){
            alert("STARS")
        };
        scope.ShowDownloaders = function(project){
            alert("DOWNLOADERS")
        };
        scope.ShowIssues = function(project){
            alert("ISSUES")
        };
        scope.ShowPullRequests = function(project){
            alert("PULL REQUESTS")
        };
        scope.ShowBadgeImpressions = function(project){
            alert("BADGE IMPRESSIONS")
        };
        scope.ShowTwitterMentions = function(project){
            alert("TWITTER MENTIONS")
        };
        scope.ShowStackoverflowTopics = function(project){
            alert("STACK OVERFLOW TOPICS")
        };

    });
});

window.INSTANCES.controller("InstancesSideBar", function($scope){

});
