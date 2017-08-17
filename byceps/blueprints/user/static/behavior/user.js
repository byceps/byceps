onDomReady(function() {

  confirmed_delete_on_click_then_reload('[data-action="avatar-delete"]', 'Avatarbild entfernen?');

  post_on_click_then_reload('[data-action="newsletter-subscribe"]');
  confirmed_delete_on_click_then_reload('[data-action="newsletter-unsubscribe"]', 'Wirklich vom Newsletter abmelden?');

});
