// Seleccionamos todas las secciones excepto #portada
const secciones = document.querySelectorAll("section:not(#portada)");

const aparecer = () => {
  secciones.forEach(sec => {
    const top = sec.getBoundingClientRect().top;
    const altura = window.innerHeight;

    if (top < altura - 100) {
      sec.style.opacity = "1";
      sec.style.transform = "translateY(0)";
    }
  });
};

// Aplicamos efecto scroll solo a las secciones interiores
window.addEventListener("scroll", aparecer);

secciones.forEach(sec => {
  sec.style.opacity = "0";
  sec.style.transform = "translateY(40px)";
  sec.style.transition = "all 0.8s ease";
});

window.addEventListener("load", () => {
  setTimeout(aparecer, 500); // Espera 0.5 segundos antes de animar
});

