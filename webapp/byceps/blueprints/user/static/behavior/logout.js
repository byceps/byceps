$(function() {
  // Log out.
  $('a#logout').click(function() {
    if (confirm('Wirklich abmelden?')) {
      $.post($(this).attr('href'), function() {
        location.href = '/';
      });
    };
    return false;
  });
});
