var APP = angular.module('Instances', []);

$(function(){
    var ADDRESS = $("body").data("socketaddress");
    var username = $("#socket-meta").data("username");

    var socket = io.connect(ADDRESS);
    var scope = angular.element($("body")).scope();

    socket.on('connect', function() {
        console.log('connected');
    });
    socket.on('error', function(e) {
        console.log('error', e);
    });
    socket.on('disconnect', function() {
        console.log('disconnected');
    });
    socket.on('visitors', function(visitos) {
        console.log('visitors', visitors);
        scope.$apply(function(){
            scope.visitors = visitors;
        });
    });
    $(".live-stats-repository").on("click", function(e){
        e.preventDefault();
        var $btn = $(this);
        var meta_id = $btn.data("meta-id");
        var raw = $(meta_id).html();
        var metadata = JSON.parse(raw);
	socket.emit('repository_statistics', {
            "username": username,
            "project": meta.name,
            "kind": "forks"
        });

    });
});

APP.controller("DashboardController", function($scope){
    $scope.connectionStatus = 'disconnected';
});
