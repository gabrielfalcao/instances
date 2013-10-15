var APP = angular.module('Instances', []).
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

$(function(){
    var ADDRESS = $("body").data("socketaddress");
    var username = $("#socket-meta").data("username");
    var context_ajax_url = $("#dashboard-meta").data("context-ajax-url");
    var modal_tracking_ajax_url = $("#dashboard-meta").data("modal-tracking-url");
    function get_modal_url(repository) {
        return modal_tracking_ajax_url.replace(username + "-PLACEHOLDER", repository.name)
    }
    var socket = io.connect(ADDRESS);
    var scope = angular.element($("body")).scope();
    function make_loader(icon_name){
        return '<div class="uk-grid uk-text-center modal-loader"><div class="uk-width-1-1 " style="padding-top: 200px;%"><h2>loading...</h2><i class="uk-icon-'+icon_name+' uk-icon-large uk-icon-spin"></i></div></div>';
    }
    scope.$apply(function(){
        scope.visitors = {};
        scope.username = username;
        scope.liveMonitorProject = function(repository){
            var payload = {
                "username": username,
                "project": repository.name
            };
            $(".live-stats-repository").removeClass("active");
            $(".live-stats-repository[data-full-name='"+repository.full_name+"']").addClass("active");

            socket.emit('repository_statistics', payload);
        };

        scope.showModal = function(repository){
            var selector = "#tracking-code-modal .uk-modal-dialog";
            $(selector).empty();
            $(selector).html(make_loader("spinner"));
            var modal = new $.UIkit.modal.Modal("#tracking-code-modal");
            modal.show();
            $.get(get_modal_url(repository), function(html){
                $(selector).html(html);
            })
        };
    });
    socket.on('connect', function() {
        console.log('connected');
    });
    socket.on('error', function(e) {
        console.log('error', e);
    });
    socket.on('disconnect', function() {
        console.log('disconnected');
        $(".live-stats-repository").removeClass("active");
        scope.$apply(function(){
            scope.visitors = null;
        });
    });
    socket.on("visitors", function(visitors) {
        scope.$apply(function(){
            scope.visitors = visitors;
        });
    });
    $(function(){
        $.getJSON(context_ajax_url, function(data){
            scope.$apply(function(){
                scope.tracked_repositories = data.tracked_repositories;
                scope.repositories = data.repositories;
                scope.repositories_by_name = data.repositories_by_name;
                $(".ajax-loader").hide();
            });
        });
    });

});

APP.controller("DashboardController", function($scope){
});
