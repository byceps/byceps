onDomReady(function() {

  // Log in.
  $('form#login').submit(function() {
    const login_failed_notice = document.getElementById('login-failed-notice');
    login_failed_notice.classList.add('hidden');

    $.ajax({
      type: 'POST',
      url: $(this).attr('action'),
      data: $(this).serializeArray(),
      success: function(data, text_status, xhr) {
        // Redirect to location specified via header.
        var redirect_url = _get_location(xhr);
        if (redirect_url !== null) {
          location.href = redirect_url;
          return;
        }

        // Redirect to referrer if available.
        var referrer = document.createElement('a');
        referrer.href = document.referrer;
        // Exclude selected referrer paths.
        if (/^\/(authentication|consent)\//.test(referrer.pathname)) {
          referrer.pathname = '/';
        }
        location.href = (referrer.hostname == location.hostname) ? referrer.pathname : '/';
      },
      error: function() {
        login_failed_notice.classList.remove('hidden');
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
            location.href = '/authentication/login';
          });
        };

        event.preventDefault();
      });
    });
});
