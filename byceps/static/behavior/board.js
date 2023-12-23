onDomReady(() => {

  const collapsedTextareas = document.querySelectorAll('textarea.collapsed');
  collapsedTextareas.forEach(textarea => {
    // Expand collapsible text area after receiving focus.
    textarea
      .addEventListener('focus', () => textarea.classList.remove('collapsed'));

    // Collapse text area on click on cancel button.
    textarea.form.querySelector('button.cancel')
      .addEventListener('click', () => textarea.classList.add('collapsed'));
  });

  document.querySelectorAll('[data-action="posting-react"]').forEach(element => {
    const indicator_class_name = 'button--reaction-active';
    element.addEventListener('click', event => {
      if (element.classList.contains(indicator_class_name)) {
        fetch(element.dataset.urlRemove, {method: 'DELETE'})
          .then(response => {
            if (response.status == 204) {
              element.dataset.count = parseInt(element.dataset.count) - 1;
              element.classList.remove(indicator_class_name);
            }
          });
      } else {
        fetch(element.dataset.urlAdd, {method: 'POST'})
          .then(response => {
            if (response.status == 204) {
              element.dataset.count = parseInt(element.dataset.count) + 1;
              element.classList.add(indicator_class_name);
            }
          });
      }

      event.preventDefault();
    });
  });

});
