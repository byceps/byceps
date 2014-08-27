$(function() {

  // Hide a posting.
  confirmed_post_on_click('a#posting-hide', 'Beitrag verstecken?');

  // Un-hide a posting.
  confirmed_delete_on_click('a#posting-unhide', 'Beitrag wieder anzeigen?');

  /* utilities */

  function confirmed_post_on_click(selector, confirmation_label) {
    _confirmed_request_on_click(selector, confirmation_label, 'POST');
  }

  function confirmed_delete_on_click(selector, confirmation_label) {
    _confirmed_request_on_click(selector, confirmation_label, 'DELETE');
  }

  function _confirmed_request_on_click(selector, confirmation_label, method) {
    $(selector).click(function() {
      if (confirm(confirmation_label)) {
        var request_url = $(this).attr('href');
        _ajax_and_redirect(method, request_url);
      };
      return false;
    });
  }

  function _ajax_and_redirect(method, request_url) {
    $.ajax({
      type: method,
      url: request_url,
      complete: function(xhr, text_status) {
        if (text_status == 'nocontent') {
          var redirect_url = _get_location(xhr);
          location.href = redirect_url;
        }
      }
    });
  }

  function _get_location(xhr) {
    return xhr.getResponseHeader('Location');
  }

});
