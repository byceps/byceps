onDomReady(() => {
  const loginForm = document.getElementById('login-form');
  if (loginForm !== null) {
    loginForm.addEventListener('submit', event => {
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

          // Extract `next` parameter from `location.search`, if available.
          const searchObject = new URLSearchParams(location.search);
          const nextParam = searchObject.get('next');
          if (nextParam !== null) {
            const nextLocation = new URL(nextParam, location.href);
            if (nextLocation.hostname == location.hostname) {
              location.href = nextLocation.pathname;
              return;
            }
          }

          // Redirect to location specified via header.
          const redirectUrl = response.headers.get('Location');
          if (redirectUrl !== null) {
            location.href = redirectUrl;
            return;
          }

          // Fallback: redirect to `/`.
          location.href = '/';
        });
    });
  }
});
