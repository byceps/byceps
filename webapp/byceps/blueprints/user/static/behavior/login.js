$(function() {
  $('form#login').submit(function() {
    $('#login-failed').slideUp('fast');
    $.ajax({
      type: 'POST',
      url: $(this).attr('action'),
      data: $(this).serializeArray(),
      success: function() {
        location.href = '/';
      },
      error: function() {
        $('#login-failed').slideDown('slow', function() {
        });
      },
      dataType: 'text'
    });
    return false;
  });
})
