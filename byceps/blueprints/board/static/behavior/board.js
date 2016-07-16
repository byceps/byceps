$(function() {

  confirmed_post_on_click('a#topic-hide', 'Thema verstecken?');
  confirmed_delete_on_click('a#topic-unhide', 'Thema wieder anzeigen?');
  confirmed_post_on_click('a#topic-lock', 'Thema schließen?');
  confirmed_delete_on_click('a#topic-unlock', 'Thema wieder öffnen?');
  confirmed_post_on_click('a#topic-pin', 'Thema anpinnen?');
  confirmed_delete_on_click('a#topic-unpin', 'Thema wieder lösen?');

  confirmed_post_on_click('a#posting-hide', 'Beitrag verstecken?');
  confirmed_delete_on_click('a#posting-unhide', 'Beitrag wieder anzeigen?');

});
