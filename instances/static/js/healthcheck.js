var APP = angular.module('Instances', []);
$(function(){
    var ADDRESS = $("body").data("socketaddress");
    var socket = io.connect(ADDRESS);
    var scope = angular.element($("body")).scope();

    socket.on('connect', function() {
        scope.$apply(function(){
            scope.connectionStatus = 'connected';
	    socket.emit('listen', 'now');
        })
    });
    socket.on('error', function(e) {
        scope.$apply(function(){
            scope.connectionStatus = 'error, check console';
        })
    });
    socket.on('disconnect', function() {
        scope.$apply(function(){
            scope.connectionStatus = 'disconnected';
        })

    });
    socket.on('status', function(msg) {
        var d = $.parseJSON(msg);
        scope.$apply(function(){
            scope.status = d;
        })
    });
});

APP.controller("InstancesController", function($scope){
    $scope.connectionStatus = 'disconnected';
});
