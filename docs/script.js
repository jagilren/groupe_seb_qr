document.addEventListener('DOMContentLoaded', function () {
    // Toggle categorías
    document.querySelectorAll('.nav-cat').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var group = btn.closest('.nav-group');
            var open = group.classList.toggle('open');
            btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
    });

    // Expandir automáticamente la categoría que contenga el link activo
    var active = document.querySelector('.nav-items a.active');
    if (active) {
        var group = active.closest('.nav-group');
        if (group) {
            group.classList.add('open');
            var btn = group.querySelector('.nav-cat');
            if (btn) btn.setAttribute('aria-expanded', 'true');
        }
    } else {
        // Si no hay activo, abrir todas para que el menú no se vea vacío
        document.querySelectorAll('.nav-group').forEach(function (g) {
            g.classList.add('open');
            var btn = g.querySelector('.nav-cat');
            if (btn) btn.setAttribute('aria-expanded', 'true');
        });
    }

    // Menú hamburguesa móvil
    var toggle = document.querySelector('.menu-toggle');
    var sidebar = document.querySelector('.sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', function () {
            sidebar.classList.toggle('open');
        });
    }
});
