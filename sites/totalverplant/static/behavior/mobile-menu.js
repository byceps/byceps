// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  const navLinks = document.querySelector('.nav-links');

  if (mobileMenuBtn && navLinks) {
    mobileMenuBtn.addEventListener('click', function() {
      const isOpen = navLinks.classList.contains('mobile-menu-open');

      navLinks.classList.toggle('mobile-menu-open');
      mobileMenuBtn.classList.toggle('active');

      // Update aria-expanded attribute
      mobileMenuBtn.setAttribute('aria-expanded', !isOpen);

      // Update button text
      const buttonText = mobileMenuBtn.querySelector('[aria-hidden]');
      if (buttonText) {
        buttonText.textContent = !isOpen ? '✕' : '☰';
      }
    });

    // Helper function to close menu
    function closeMenu() {
      navLinks.classList.remove('mobile-menu-open');
      mobileMenuBtn.classList.remove('active');
      mobileMenuBtn.setAttribute('aria-expanded', 'false');
      const buttonText = mobileMenuBtn.querySelector('[aria-hidden]');
      if (buttonText) {
        buttonText.textContent = '☰';
      }
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
      if (!event.target.closest('.nav-links') &&
          !event.target.closest('.mobile-menu-btn') &&
          navLinks.classList.contains('mobile-menu-open')) {
        closeMenu();
      }
    });

    // Close mobile menu when clicking a link
    const navLinksItems = navLinks.querySelectorAll('a');
    navLinksItems.forEach(function(link) {
      link.addEventListener('click', function() {
        closeMenu();
      });
    });

    // Close mobile menu when pressing Escape key
    document.addEventListener('keydown', function(event) {
      if (event.key === 'Escape' && navLinks.classList.contains('mobile-menu-open')) {
        closeMenu();
        mobileMenuBtn.focus(); // Return focus to button
      }
    });
  }
});