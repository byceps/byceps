$(function() {

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
