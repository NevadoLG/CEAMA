// Función para desplazarse a la sección de contacto
function scrollToContacto() {
  const contactoSection = document.getElementById("contacto")
  contactoSection.scrollIntoView({ behavior: "smooth" })
}

// Agregar efecto de scroll a la navegación
window.addEventListener("scroll", () => {
  const header = document.querySelector(".header")
  if (window.scrollY > 50) {
    header.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.1)"
  } else {
    header.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.05)"
  }
})

// Resaltar enlace de navegación activo
document.querySelectorAll(".nav a").forEach((link) => {
  link.addEventListener("click", function (e) {
    document.querySelectorAll(".nav a").forEach((a) => (a.style.color = ""))
    this.style.color = "var(--primary)"
  })
})
