$(function() {

  $('.dropdown .dropdown-toggle').click(function() {
    $(this).parent().toggleClass('open');
    return false;
  });

  $(document).click(function(event) {
    // For details, see: https://css-tricks.com/dangers-stopping-event-propagation/
    if (!$(event.target).closest('.dropdown').length) {
      $('.dropdown.open').removeClass('open');
    }
  });

});
