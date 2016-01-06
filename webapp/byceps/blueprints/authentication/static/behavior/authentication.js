$(function() {

  // Log in.
  $('form#login').submit(function() {
    $('#login-failed').slideUp('fast');
    $.ajax({
      type: 'POST',
      url: $(this).attr('action'),
      data: $(this).serializeArray(),
      success: function() {
        location.href = '/';
      },
      error: function() {
        $('#login-failed').slideDown('slow', function() {
        });
      },
      dataType: 'text'
    });
    return false;
  });

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
