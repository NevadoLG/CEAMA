(() => {
  document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-pago');
    const btn  = document.getElementById('btn-registrar');
    const inputArchivos = document.getElementById('id_archivos');
    const MAX = 3;

    // Evitar doble envío
    if (form && btn) {
      form.addEventListener('submit', () => {
        if (btn.disabled) return;
        btn.disabled = true;
        btn.textContent = 'Registrando...';
      });
    }

    // Vista previa (con X para quitar) + límite de 3
    if (inputArchivos) {
      // contenedor de previews (lo creamos una sola vez)
      let previewGrid = document.getElementById('preview-grid');
      if (!previewGrid) {
        previewGrid = document.createElement('div');
        previewGrid.id = 'preview-grid';
        previewGrid.className = 'preview-grid';
        // lo insertamos debajo del input
        inputArchivos.closest('.form-group')?.appendChild(previewGrid);
      }

      inputArchivos.addEventListener('change', (e) => {
        const files = Array.from(e.target.files || []);
        // si excede el máximo, cortamos y avisamos
        if (files.length > MAX) {
          alert(`Solo puedes adjuntar hasta ${MAX} archivos.`);
          // nos quedamos con los primeros MAX
          const dt = new DataTransfer();
          files.slice(0, MAX).forEach(f => dt.items.add(f));
          inputArchivos.files = dt.files;
        }
        renderPreviews(Array.from(inputArchivos.files));
      });

      function renderPreviews(files) {
        previewGrid.innerHTML = '';
        files.forEach((file, idx) => {
          const item = document.createElement('div');
          item.className = 'preview-item';

          // Botón de eliminar (X)
          const removeBtn = document.createElement('button');
          removeBtn.type = 'button';
          removeBtn.className = 'preview-remove';
          removeBtn.textContent = '×';
          removeBtn.title = 'Quitar';

          removeBtn.addEventListener('click', () => {
            // quitar el archivo idx del FileList usando DataTransfer
            const current = Array.from(inputArchivos.files);
            current.splice(idx, 1);
            const dt = new DataTransfer();
            current.forEach(f => dt.items.add(f));
            inputArchivos.files = dt.files;
            renderPreviews(current);
          });

          // imagen vs pdf/otros
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

          item.appendChild(removeBtn);
          previewGrid.appendChild(item);
        });
      }
    }
  });
})();
