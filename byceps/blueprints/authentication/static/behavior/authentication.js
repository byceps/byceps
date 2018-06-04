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
  forEach(
    document.querySelectorAll('a[data-action="logout"]'),
    function(anchor) {
      anchor.addEventListener('click', function(event) {
        if (confirm('Wirklich abmelden?')) {
          const href = anchor.getAttribute('href');
          send_post_request(href, function() {
            location.href = '/';
          });
        };

        event.preventDefault();
      });
    });
});
