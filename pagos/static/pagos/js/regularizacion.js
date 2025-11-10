(() => {
  document.addEventListener('DOMContentLoaded', () => {
    const form  = document.getElementById('form-regularizacion');
    if (!form) return;

    const fileInput = document.getElementById('id_archivos'); // name fijo
    const btnSubmit = document.getElementById('btn-regularizar');
    const montoInput = form.querySelector('input[name="monto"]');
    const MAX = parseInt(fileInput?.dataset?.max || '3', 10);

    function clampMonto() {
      if (!montoInput) return;
      let v = (montoInput.value || '').toString().replace(',', '.');
      let n = parseFloat(v);
      if (isNaN(n) || n < 1) n = 1;
      if (n > 999.99) n = 999.99;
      montoInput.value = n.toFixed(2);
    }
    montoInput?.addEventListener('blur', clampMonto);
    montoInput?.addEventListener('change', clampMonto);
    montoInput?.addEventListener('input', () => {
      const v = (montoInput.value || '').toString().replace(',', '.');
      const n = parseFloat(v);
      if (!isNaN(n) && n > 999.99) montoInput.value = '999.99';
    });

    form.addEventListener('submit', () => {
      clampMonto();
      if (btnSubmit) {
        btnSubmit.disabled = true;
        btnSubmit.textContent = 'Enviando...';
      }
    });

    const grid = document.getElementById('preview-grid');
    function render(files) {
      if (!grid) return;
      grid.innerHTML = '';
      files.forEach((file, idx) => {
        const item = document.createElement('div');
        item.className = 'preview-item';

        const remove = document.createElement('button');
        remove.type = 'button';
        remove.className = 'preview-remove';
        remove.title = 'Quitar';
        remove.textContent = '×';
        remove.addEventListener('click', () => {
          const arr = Array.from(fileInput.files);
          arr.splice(idx, 1);
          const dt = new DataTransfer();
          arr.forEach(f => dt.items.add(f));
          fileInput.files = dt.files;
          render(arr);
        });

        if (file.type.startsWith('image/')) {
          const img = document.createElement('img');
          img.src = URL.createObjectURL(file);
          img.onload = () => URL.revokeObjectURL(img.src);
          item.appendChild(img);
        } else if (file.type === 'application/pdf') {
          const box = document.createElement('div');
          box.className = 'preview-pdf';
          box.textContent = `PDF: ${file.name}`;
          item.appendChild(box);
        } else {
          const box = document.createElement('div');
          box.className = 'preview-other';
          box.textContent = file.name;
          item.appendChild(box);
        }

        item.appendChild(remove);
        grid.appendChild(item);
      });
    }

    if (fileInput) {
      fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files || []);
        if (files.length > MAX) {
          alert(`Solo puedes adjuntar hasta ${MAX} archivos.`);
          const dt = new DataTransfer();
          files.slice(0, MAX).forEach(f => dt.items.add(f));
          fileInput.files = dt.files;
        }
        render(Array.from(fileInput.files));
      });
    }
  });
})();
