var APP = angular.module('Instances', []);

$(function(){
    var ADDRESS = $("body").data("socketaddress");
    var socket = io.connect(ADDRESS);
    var scope = angular.element($("body")).scope();

    var worldMap = SimpleMapD3({
        container: '.simple-map-d3-world-map',
        datasource: $("body").data('world-map-url'),
        projection: 'equirectangular',
        colorOn: true,
        colorProperty: 'POP2005',
        colorSet: 'Paired',
        colorScale: 'quantize',
        tooltipOn: true,
        graticuleOn: true,
        globeOn: true,
        legendOn: false,
        startManually: true
    }).start();
});

APP.controller("DashboardController", function($scope){
    $scope.connectionStatus = 'disconnected';
});
