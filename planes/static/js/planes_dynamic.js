(function () {
  function gradoANivel(grado) {
    if (!grado) return 'primaria';
    const g = grado.toLowerCase();
    return (g.includes('sec')) ? 'secundaria' : 'primaria';
  }

  async function cargarPlanes(nivel, endpoint, selectPlan) {
    selectPlan.innerHTML = '';
    selectPlan.disabled = true;

    try {
      const url = `${endpoint}?nivel=${encodeURIComponent(nivel)}`;
      const res = await fetch(url, { credentials: 'same-origin' });
      const planes = await res.json();

      if (!planes.length) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'No hay planes para el grado seleccionado';
        selectPlan.appendChild(opt);
        selectPlan.disabled = true;
        return;
      }

      const frag = document.createDocumentFragment();
      planes.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.nombre;
        frag.appendChild(opt);
      });
      selectPlan.appendChild(frag);
      selectPlan.disabled = false;
    } catch (e) {
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = 'Error cargando planes';
      selectPlan.appendChild(opt);
      selectPlan.disabled = true;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const gradoSel = document.getElementById('grado');
    const planSel  = document.getElementById('plan');
    if (!gradoSel || !planSel) return;

    const endpoint = planSel.dataset.endpoint; // viene del template

    cargarPlanes(gradoANivel(gradoSel.value), endpoint, planSel);

    gradoSel.addEventListener('change', () => {
      cargarPlanes(gradoANivel(gradoSel.value), endpoint, planSel);
    });
  });
})();
