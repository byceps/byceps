$(function() {

  // Open dropdown if user clicks on dropdown trigger.
  document.querySelectorAll('.dropdown .dropdown-toggle').forEach(function(triggerElement) {
    triggerElement.addEventListener('click', function(event) {
      var dropdown = triggerElement.parentNode;
      dropdown.classList.toggle('open');

      event.preventDefault();
    });
  });

  // Close open dropdowns if user clicks outside of an open dropdown.
  document.addEventListener('click', function(event) {
    var openDropdowns = document.querySelectorAll('.dropdown.open');
    openDropdowns.forEach(function(openDropdown) {
      if (!openDropdown.contains(event.target)) {
        openDropdown.classList.remove('open');
      }
    });
  });

});
