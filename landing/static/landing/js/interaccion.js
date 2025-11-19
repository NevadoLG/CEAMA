/**
 * Lógica de interacción para la nueva landing page (Adaptada de Lovable)
 * Implementa el menú móvil y el scroll suave entre secciones.
 */

// Función para desplazarse a la sección por ID (usada por la Navbar)
function scrollToSection(id) {
    const element = document.getElementById(id);
    element?.scrollIntoView({ behavior: "smooth" });
}

// Lógica de toggle para el menú móvil
document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIcon = document.getElementById('menu-icon');
    const xIcon = document.getElementById('x-icon');

    if (toggleButton && mobileMenu) {
        toggleButton.addEventListener('click', () => {
            const isOpen = mobileMenu.classList.contains('hidden');
            if (isOpen) {
                // Abrir menú (mostrar menú, ocultar ícono de menú, mostrar ícono X)
                mobileMenu.classList.remove('hidden');
                menuIcon?.classList.add('hidden');
                xIcon?.classList.remove('hidden');
            } else {
                // Cerrar menú
                mobileMenu.classList.add('hidden');
                menuIcon?.classList.remove('hidden');
                xIcon?.classList.add('hidden');
            }
        });
    }
});

// Función auxiliar para cerrar el menú móvil (usada en los enlaces del menú)
function closeMobileMenu() {
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIcon = document.getElementById('menu-icon');
    const xIcon = document.getElementById('x-icon');
    
    if (mobileMenu) {
        mobileMenu.classList.add('hidden');
        menuIcon?.classList.remove('hidden');
        xIcon?.classList.add('hidden');
    }
}