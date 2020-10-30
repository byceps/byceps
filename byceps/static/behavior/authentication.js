onDomReady(function() {

  // Log in.
  const loginForm = document.getElementById('login-form');
  if (loginForm !== null) {
    loginForm.addEventListener('submit', function(event) {
      event.preventDefault();

      const loginFailedNotice = document.getElementById('login-failed-notice');
      loginFailedNotice.classList.add('hidden');

      const authUrl = loginForm.getAttribute('action');
      const formData = new FormData(loginForm);

      fetch(authUrl, {
        method: 'POST',
        body: formData,
      })
        .then(response => {
          if (!response.ok) {
            loginFailedNotice.classList.remove('hidden');
            return;
          }

          // Redirect to location specified via header.
          const redirectUrl = response.headers.get('Location');
          if (redirectUrl !== null) {
            location.href = redirectUrl;
            return;
          }

          // Redirect to referrer if available.
          const referrer = document.createElement('a');
          referrer.href = document.referrer;
          // Exclude selected referrer paths.
          if (/^\/(authentication|consent)\//.test(referrer.pathname)) {
            referrer.pathname = '/';
          }
          location.href = (referrer.hostname == location.hostname) ? referrer.pathname : '/';
        });
    });
  }

});
