/**
 * Provide an alternative `forEach` function as `NodeList.forEach` is
 * not available on Firefox < v50 and MSIE.
 */
function forEach(array, callback, scope) {
  for (var i = 0; i < array.length; i++) {
    callback.call(scope, array[i]);
  }
};


/**
 * Register a function to be called when the document is "ready", i.e.
 * all the markup has been placed on the page.
 *
 * It does not wait until additional resources (stylesheets, images,
 * subframes) have been loaded.
 */
function onDomReady(callback) {
  if (document.readyState === 'complete' || document.readyState !== 'loading') {
    // The document has already fully loaded.
    callback();
  } else {
    document.addEventListener('DOMContentLoaded', callback);
  }
}



function post_on_click(selector) {
  _request_on_click(selector, 'POST');
}

function post_on_click_then_reload(selector) {
  _request_on_click_then_reload(selector, 'POST');
}

function confirmed_post_on_click(selector, confirmation_label) {
  _confirmed_request_on_click(selector, confirmation_label, 'POST');
}

function confirmed_post_on_click_then_reload(selector, confirmation_label) {
  _confirmed_request_on_click_then_reload(selector, confirmation_label, 'POST');
}

function confirmed_delete_on_click(selector, confirmation_label) {
  _confirmed_request_on_click(selector, confirmation_label, 'DELETE');
}

function confirmed_delete_on_click_then_reload(selector, confirmation_label) {
  _confirmed_request_on_click_then_reload(selector, confirmation_label, 'DELETE');
}

function _request_on_click(selector, method) {
  $(selector).click(function() {
    var request_url = $(this).attr('href');
    _ajax_then_redirect_to_location_response_header(method, request_url);
    return false;
  });
}

function _request_on_click_then_reload(selector, method) {
  $(selector).click(function() {
    var request_url = $(this).attr('href');
    _ajax_then_reload(method, request_url);
    return false;
  });
}

function _confirmed_request_on_click(selector, confirmation_label, method) {
  $(selector).click(function() {
    if (confirm(confirmation_label)) {
      var request_url = $(this).attr('href');
      _ajax_then_redirect_to_location_response_header(method, request_url);
    };
    return false;
  });
}

function _confirmed_request_on_click_then_reload(selector, confirmation_label, method) {
  $(selector).click(function() {
    if (confirm(confirmation_label)) {
      var request_url = $(this).attr('href');
      _ajax_then_reload(method, request_url);
    };
    return false;
  });
}

function _ajax_then_redirect_to_location_response_header(method, request_url) {
  _ajax(method, request_url, function(xhr, text_status) {
    if (text_status == 'nocontent') {
      var redirect_url = _get_location(xhr);
      location.href = redirect_url;
    }
  });
}

function _ajax_then_reload(method, request_url) {
  _ajax(method, request_url, function(xhr, text_status) {
    if (text_status == 'nocontent') {
      location.href = location.href;
    }
  });
}

function _ajax(method, request_url, on_complete) {
  $.ajax({
    type: method,
    url: request_url,
    complete: on_complete
  });
}

function _get_location(xhr) {
  return xhr.getResponseHeader('Location');
}


/**
 * Add behavior to dropdown menus.
 */
onDomReady(function() {

  // Open dropdown if user clicks on dropdown trigger.
  var dropdownToggles = document.querySelectorAll('.dropdown .dropdown-toggle');
  forEach(dropdownToggles, function(triggerElement) {
    triggerElement.addEventListener('click', function(event) {
      var dropdown = triggerElement.parentNode;
      dropdown.classList.toggle('open');

      event.preventDefault();
    });
  });

  // Close open dropdowns if user clicks outside of an open dropdown.
  document.addEventListener('click', function(event) {
    var openDropdowns = document.querySelectorAll('.dropdown.open');
    forEach(openDropdowns, function(openDropdown) {
      if (!openDropdown.contains(event.target)) {
        openDropdown.classList.remove('open');
      }
    });
  });

});


/**
 * Register an element as click trigger to copy the value of a field to
 * the clipboard.
 */
function enableCopyToClipboard(field, triggerElement) {
  triggerElement.addEventListener('click', function() {
    field.focus();
    field.select();
    try {
      document.execCommand('copy');
    } catch (err) {}
    field.blur();
  });
}
