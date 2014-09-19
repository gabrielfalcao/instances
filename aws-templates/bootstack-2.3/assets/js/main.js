jQuery(document).ready(function() {

  /* Active Links */
  var sections = $("section"),
  navigation_links = $("#navigation a");

  sections.waypoint( {
    handler: function(event, direction) {
      var active_section;

      active_section = $(this);
      if (direction === "up") active_section = active_section.prev();

      var active_link = $('#navigation a[href="#' + active_section.attr("id") + '"]');

      navigation_links.parent().removeClass("active");
      active_link.parent().addClass("active");
    },
    offset: '50%'
  });


  /* Right navigation collapses navbar in mobile view */
  $(function() {
    $('#navigation a').on('click', function(){
      if ($('.navbar-toggle').css('display') !='none'){
        $(".navbar-toggle").trigger( "click" );
      }
    });
  });

  /*
  $("body").click(function(event) {
    // only do this if navigation is visible, otherwise you see jump in navigation while collapse() is called 
     if ($(".navbar-collapse").is(":visible") && $(".navbar-toggle").is(":visible") ) {
      $('.navbar-collapse').collapse('toggle');
      e.stopPropgation();
      event.defaultPrevented();
    }
  });
  */


  /* Scroll to top */
  $('body').append('<div id="back-top"><span class="icon-arrow-up2"></span></div>');
  $("#back-top").hide();

  // fade in #back-top
  $(function () {
    $(window).scroll(function () {
      if ($(this).scrollTop() > 100) {
      $('#back-top').fadeIn();
      } else {
      $('#back-top').fadeOut();
      }
    });

    // scroll body to 0px on click
    $('#back-top').click(function () {
      $('body,html').animate({
      scrollTop: 0
      }, 800);
      return false;
    });
  });


  /* Remove navbar button 'pull-left' class on mobile */
  var width = $(window).width();
  if (width < 768) {
    $('.navbar-form').removeClass('pull-left');
    $('.navbar-form').css({'border' : '0'});
  }


  /* IE 10 in Windows 8 and Windows Phone 8 fix */
  if (navigator.userAgent.match(/IEMobile\/10\.0/)) {
    var msViewportStyle = document.createElement('style')
    msViewportStyle.appendChild(
      document.createTextNode(
          '@-ms-viewport{width:auto!important}'
        )
    )
    document.querySelector('head').appendChild(msViewportStyle)
  }


  /* Android stock browser fix */
  var nua = navigator.userAgent
  var isAndroid = (nua.indexOf('Mozilla/5.0') > -1 && nua.indexOf('Android ') > -1 && nua.indexOf('AppleWebKit') > -1 && nua.indexOf('Chrome') === -1)
  if (isAndroid) {
    $('select.form-control').removeClass('form-control').css('width', '100%')
  }

});
