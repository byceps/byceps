$(function() {

  confirmed_post_on_click('[data-action="topic-hide"]', 'Thema verstecken?');
  confirmed_delete_on_click('[data-action="topic-unhide"]', 'Thema wieder anzeigen?');
  confirmed_post_on_click('[data-action="topic-lock"]', 'Thema schließen?');
  confirmed_delete_on_click('[data-action="topic-unlock"]', 'Thema wieder öffnen?');
  confirmed_post_on_click('[data-action="topic-pin"]', 'Thema anpinnen?');
  confirmed_delete_on_click('[data-action="topic-unpin"]', 'Thema wieder lösen?');

  confirmed_post_on_click('[data-action="posting-hide"]', 'Beitrag verstecken?');
  confirmed_delete_on_click('[data-action="posting-unhide"]', 'Beitrag wieder anzeigen?');

});
