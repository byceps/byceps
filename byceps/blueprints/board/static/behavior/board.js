$(function() {

  confirmed_post_on_click('[data-action="topic-hide"]', 'Thema verstecken?');
  confirmed_delete_on_click('[data-action="topic-unhide"]', 'Thema wieder anzeigen?');
  confirmed_post_on_click('[data-action="topic-lock"]', 'Thema schließen?');
  confirmed_delete_on_click('[data-action="topic-unlock"]', 'Thema wieder öffnen?');
  confirmed_post_on_click('[data-action="topic-pin"]', 'Thema anpinnen?');
  confirmed_delete_on_click('[data-action="topic-unpin"]', 'Thema wieder lösen?');

  confirmed_post_on_click('[data-action="posting-hide"]', 'Beitrag verstecken?');
  confirmed_delete_on_click('[data-action="posting-unhide"]', 'Beitrag wieder anzeigen?');

  var collpasedTextareas = document.querySelectorAll('textarea.collapsed');
  forEach(collpasedTextareas, function(element) {
    // Expand collapsible text areas after receiving focus.
    element.addEventListener('focus', function() {
      element.classList.remove('collapsed');
    });

    // Collapse *empty* text areas after losing focus.
    element.addEventListener('blur', function() {
      if (element.value == '') {
        element.classList.add('collapsed');
      }
    });
  });

});
