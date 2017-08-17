onDomReady(function() {

  // Log in.
  $('form#login').submit(function() {
    $('#login-failed').slideUp('fast');
    $.ajax({
      type: 'POST',
      url: $(this).attr('action'),
      data: $(this).serializeArray(),
      success: function() {
        // Redirect to referrer if available.
        var referrer = document.createElement('a');
        referrer.href = document.referrer;
        location.href = (referrer.hostname == location.hostname) ? referrer.pathname : '/';
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
  $('[data-action="logout"]').click(function() {
    if (confirm('Wirklich abmelden?')) {
      $.post($(this).attr('href'), function() {
        location.href = '/';
      });
    };
    return false;
  });

});
