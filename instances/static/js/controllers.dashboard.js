var APP = angular.module('instances', []).
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
        scope.current_project = false;
        scope.username = username;
        scope.liveMonitorProject = function(repository){
            scope.current_project = repository.full_name;
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
        var colors = ["#EDF8B1",
                      "#7FCDBB",
                      "#2C7FB8",
                      "#0E4C78"]

        for (var country_code in visitors.by_country) {
            var inline_visitors = visitors.by_country[country_code];
            var country_selector = "svg.map .country[data-code='"+country_code+"']";
            var current_color = colors.shift();
            colors.push(current_color);
            var total = inline_visitors.length;
            $(country_selector).attr("style", 'stroke-width: 4;fill: ' + current_color);
            console.log(visitors)
            var tooltip_text = visitors.geo.country_name + " - " + total + " visitors";
            console.log(tooltip_text);
            $(country_selector).attr("original-title", tooltip_text);
        }

        scope.$apply(function(){
            scope.visitors = visitors;
            if (visitors.repository.full_name === scope.current_project) {
                socket.emit("repository_statistics", visitors.original_payload);
                return;
            }

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
