document.addEventListener('DOMContentLoaded', function() {
    // Toggle submenu
    const categoryLinks = document.querySelectorAll('.nav-category > a');
    
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const submenu = this.nextElementSibling;
            if (submenu && submenu.classList.contains('nav-submenu')) {
                e.preventDefault();
                submenu.style.display = submenu.style.display === 'none' ? 'block' : 'none';
            }
        });
    });
    
    // Highlight active page
    const currentPath = window.location.pathname;
    const allLinks = document.querySelectorAll('.nav-menu a');
    
    allLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.background = '#e8f0fe';
            link.style.color = '#1a73e8';
        }
    });
});