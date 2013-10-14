var APP = angular.module('Instances', []);

$(function(){
    var ADDRESS = $("body").data("socketaddress");
    var username = $("#socket-meta").data("username");

    var socket = io.connect(ADDRESS);
    var scope = angular.element($("body")).scope();
    scope.$apply(function(){
        scope.visitors = {};
    });

    socket.on('connect', function() {
        console.log('connected');
    });
    socket.on('error', function(e) {
        console.log('error', e);
    });
    socket.on('disconnect', function() {
        console.log('disconnected');
    });
    socket.on("visitors", function(visitors) {
        console.log('visitors', visitors);
        scope.$apply(function(){
            scope.visitors = visitors;
        });
    });

    $(".live-stats-repository").on("click", function(e){
        e.preventDefault();
        var $btn = $(this);
        var $li = $btn.parents("li");
        $li.siblings().removeClass("active");
        $li.addClass("active");
        var meta_id = $btn.data("meta-id");
        var raw = $(meta_id).html();

        var repository = JSON.parse(raw);
        var payload = {
            "username": username,
            "project": repository.name
        };
	socket.emit('repository_statistics', payload);
    });
});

APP.controller("DashboardController", function($scope){
    $scope.connectionStatus = 'disconnected';
});
