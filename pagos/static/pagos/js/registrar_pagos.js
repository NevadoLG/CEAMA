(() => {
  document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-pago');
    const btn  = document.getElementById('btn-registrar');
    const inputArchivos = document.getElementById('id_archivos');
    const MAX = 3;

    if (form && btn) {
      form.addEventListener('submit', () => {
        if (btn.disabled) return;
        btn.disabled = true;
        btn.textContent = 'Registrando...';
      });
    }

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

    const metodoSelect = document.getElementById('id_metodo');
    const metodoInfo   = document.getElementById('metodo-info');
    const estadoSelect = document.getElementById('id_estado');
    const montoInput   = document.getElementById('id_monto');

    const MENSAJES_METODO = {
      transferencia: 'Transfiere a la cuenta: 00257019713717601206',
      yape:          'Yapea al número: 904 929 929',
      plin:          'Envía tu Plin al número: 904 929 929',
    };

    function actualizarMensajeMetodo() {
      if (!metodoSelect || !metodoInfo) return;
      const value = metodoSelect.value;
      const msg = MENSAJES_METODO[value];
      if (msg) {
        metodoInfo.textContent = msg;
        metodoInfo.style.display = 'block';
      } else {
        metodoInfo.textContent = '';
        metodoInfo.style.display = 'none';
      }
    }

    const tarjetas = document.querySelectorAll('[data-precio-asignacion]');
    let precioTotal = 0;
    tarjetas.forEach((card) => {
      const val = parseFloat(card.getAttribute('data-precio-asignacion') || '0');
      if (!isNaN(val)) {
        precioTotal += val;
      }
    });

    function actualizarMontoPorEstado() {
      if (!estadoSelect || !montoInput) return;

      if (!precioTotal || precioTotal <= 0) {
        montoInput.readOnly = false;
        return;
      }

      if (estadoSelect.value === 'completado') {
        montoInput.value = precioTotal.toFixed(2);
        montoInput.readOnly = true;
      } else if (estadoSelect.value === 'parcial') {
        montoInput.readOnly = false;
      }
    }

    actualizarMensajeMetodo();
    actualizarMontoPorEstado();

    // Listeners
    if (metodoSelect) {
      metodoSelect.addEventListener('change', actualizarMensajeMetodo);
    }
    if (estadoSelect) {
      estadoSelect.addEventListener('change', actualizarMontoPorEstado);
    }
  });
})();
