$(function() {

  // Hide a posting.
  $('a#posting-hide').click(function() {
    if (confirm('Beitrag verstecken?')) {
      var request_url = $(this).attr('href');
      post_and_redirect(request_url);
    };
    return false;
  });

  // Un-hide a posting.
  $('a#posting-unhide').click(function() {
    if (confirm('Beitrag wieder anzeigen?')) {
      var request_url = $(this).attr('href');
      delete_and_redirect(request_url);
    };
    return false;
  });

  /* utilities */

  function post_and_redirect(request_url) {
    ajax_and_redirect('POST', request_url);
  }

  function delete_and_redirect(request_url) {
    ajax_and_redirect('DELETE', request_url);
  }

  function ajax_and_redirect(method, request_url) {
    $.ajax({
      type: method,
      url: request_url,
      complete: function(xhr, text_status) {
        if (text_status == 'nocontent') {
          var redirect_url = get_location(xhr);
          location.href = redirect_url;
        }
      }
    });
  }

  function get_location(xhr) {
    return xhr.getResponseHeader('Location');
  }

});
