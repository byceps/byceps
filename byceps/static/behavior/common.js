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


// ---------------------------------------------------------------------
// XHR requests

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

function delete_on_click(selector) {
  _request_on_click(selector, 'DELETE');
}

function delete_on_click_then_reload(selector) {
  _request_on_click_then_reload(selector, 'DELETE');
}

function confirmed_delete_on_click(selector, confirmation_label) {
  _confirmed_request_on_click(selector, confirmation_label, 'DELETE');
}

function confirmed_delete_on_click_then_reload(selector, confirmation_label) {
  _confirmed_request_on_click_then_reload(selector, confirmation_label, 'DELETE');
}

function _request_on_click(selector, method) {
  _onClickCallbackWithHref(selector, function(href) {
    _ajax_then_redirect_to_location_response_header(method, href);
  });
}

function _request_on_click_then_reload(selector, method) {
  _onClickCallbackWithHref(selector, function(href) {
    _ajax_then_reload(method, href);
  });
}

function _confirmed_request_on_click(selector, confirmation_label, method) {
  _onClickCallbackWithHref(selector, function(href) {
    if (confirm(confirmation_label)) {
      _ajax_then_redirect_to_location_response_header(method, href);
    };
  });
}

function _confirmed_request_on_click_then_reload(selector, confirmation_label, method) {
  _onClickCallbackWithHref(selector, function(href) {
    if (confirm(confirmation_label)) {
      _ajax_then_reload(method, href);
    };
  });
}


function _onClickCallbackWithHref(selector, callback) {
  const elements = document.querySelectorAll(selector);
  elements.forEach(function(element) {
    element.addEventListener('click', function(event) {
      const href = element.getAttribute('href');
      callback(href);

      event.preventDefault();
    });
  });
}

function _ajax_then_redirect_to_location_response_header(method, request_url) {
  _ajax(method, request_url, function(response) {
    if (response.status == 204) {
      const redirectUrl = response.headers.get('Location');
      if (redirectUrl !== null) {
        location.href = redirectUrl;
      }
    }
  });
}

function _ajax_then_reload(method, request_url) {
  _ajax(method, request_url, function(response) {
    if (response.status == 204) {
      location.href = location.href;
    }
  });
}

function _ajax(method, url, on_complete) {
  fetch(url, {method: method})
    .then(response => on_complete(response));
}


// ---------------------------------------------------------------------
// dropdown menus


/**
 * Make dropdown menus open if their respective trigger is clicked.
 */
function enableDropdownMenuToggles() {
  const dropdownToggles = document.querySelectorAll('.dropdown .dropdown-toggle');
  dropdownToggles.forEach(function(triggerElement) {
    triggerElement.addEventListener('click', function(event) {
      const dropdown = triggerElement.parentNode;
      dropdown.classList.toggle('open');

      event.preventDefault();
    });
  });
}


/**
 * Close all open dropdown menus but the one that has been clicked (if
 * any).
 */
function closeOpenDropdownMenus(clickTarget) {
  const openDropdowns = document.querySelectorAll('.dropdown.open');
  openDropdowns.forEach(function(openDropdown) {
    if (!openDropdown.contains(clickTarget)) {
      // Click was outside of this dropdown menu, so close it.
      openDropdown.classList.remove('open');
    }
  });
}


// Add behavior to dropdown menus.
onDomReady(function() {
  enableDropdownMenuToggles();

  // Close open dropdowns if user clicks outside of an open dropdown.
  document.addEventListener('click', function(event) {
    closeOpenDropdownMenus(event.target);
  });
});


// ---------------------------------------------------------------------
// clipboard


/**
 * Register an element as click trigger to copy the value of a field to
 * the clipboard.
 */
function enableCopyToClipboard(triggerElementId) {
  const triggerElement = document.getElementById(triggerElementId);

  triggerElement.addEventListener('click', function() {
    const fieldId = this.dataset.fieldId;
    const field = document.getElementById(fieldId);

    field.focus();
    field.select();
    try {
      document.execCommand('copy');
    } catch (err) {}
    field.blur();
  });
}


// ---------------------------------------------------------------------
// forms


// Disable the submit button of forms with class
// `disable-submit-button-on-submit` on submit.
onDomReady(function() {
  const formsWhoseSubmitButtonShouldBeDisabledOnSubmit = document
      .querySelectorAll('form.disable-submit-button-on-submit');

  formsWhoseSubmitButtonShouldBeDisabledOnSubmit.forEach(function(form) {
    form.addEventListener('submit', function() {
      const submitButton = form.querySelector('button[type="submit"]');
      submitButton.disabled = true;
      submitButton.innerHTML += ' <svg class="icon spinning"><use xlink:href="/static/style/icons.svg#spinner"></use></svg>';
    });
  });
});
