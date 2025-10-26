// Archivo: static/js/menuproducto.js
// VERSIÓN FINAL Y CORRECTA - NO USA localStorage, USA fetch() para hablar con Django

document.addEventListener("DOMContentLoaded", function () {

  console.log("✅ menuproducto.js (versión final DB) cargado correctamente");

  document.querySelectorAll('.agregar-carrito').forEach(function (btn) {
    btn.addEventListener('click', function (event) {
      event.preventDefault();

      let productCard = btn.closest('.product');
      let img = productCard.querySelector('img').src;
      let title = productCard.querySelector('h3').innerText;
      let desc = productCard.querySelector('p').innerText;
      let id = btn.getAttribute('data-id');

      // --- Llenamos el contenido del modal ---
      let modalBody = document.getElementById('modal-body-content');
      modalBody.innerHTML = `
        <div class="product-modal-body d-flex">
          <img src="${img}" class="product-modal-img me-3" alt="${title}" style="width:120px;height:auto;border-radius:8px;">
          <div class="product-modal-details">
            <h5 class="fw-bold mb-1">${title}</h5>
            <p class="text-muted mb-2">${desc}</p>
            <div class="product-modal-opciones mb-3">
              <label class="d-block"><input type="radio" name="peso-${id}" value="12" checked> 12 KG</label>
              <label class="d-block"><input type="radio" name="peso-${id}" value="4"> 4 KG</label>
            </div>
            <div class="product-modal-cantidad d-flex align-items-center gap-2">
              <label for="cant-${id}" class="mb-0">Cantidad:</label>
              <button type="button" id="menos-${id}" class="btn btn-outline-secondary btn-sm">-</button>
              <input type="number" id="cant-${id}" min="1" value="1" style="width:60px;text-align:center;">
              <button type="button" id="mas-${id}" class="btn btn-outline-secondary btn-sm">+</button>
            </div>
          </div>
        </div>`;

      // --- Asignamos funciones a los botones de cantidad (+ y -) ---
      const input = document.getElementById(`cant-${id}`);
      document.getElementById(`menos-${id}`).onclick = () => {
        if (Number(input.value) > 1) input.value = Number(input.value) - 1;
      };
      document.getElementById(`mas-${id}`).onclick = () => {
        input.value = Number(input.value) + 1;
      };

      // --- Mostramos el modal ---
      let modal = new bootstrap.Modal(document.getElementById('productoModal'));
      modal.show();

      // --- Lógica para el botón "Añadir al carrito" DENTRO del modal ---
      const btnAdd = document.querySelector('#productoModal .btn.btn-primary');
      const nuevoBtnAdd = btnAdd.cloneNode(true);
      btnAdd.parentNode.replaceChild(nuevoBtnAdd, btnAdd);
      
      nuevoBtnAdd.addEventListener('click', () => {
        const cantidad = Number(document.getElementById(`cant-${id}`).value);
        const pesoSeleccionado = document.querySelector(`input[name="peso-${id}"]:checked`).value;
        
        const productoParaEnviar = { id: id, cantidad: cantidad, peso: `${pesoSeleccionado} KG` };

        // --- ENVIAMOS LOS DATOS A DJANGO ---
        fetch('/carrito/agregar/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN 
          },
          body: JSON.stringify(productoParaEnviar)
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success') {
            window.dispatchEvent(new Event("carritoActualizado"));
            modal.hide();
            mostrarAlerta("✅ Producto añadido al carrito");
          } else {
            console.error("Error del servidor:", data.message);
            mostrarAlerta("❌ Hubo un error al añadir el producto");
          }
        })
        .catch(error => {
          console.error('Error en la petición fetch:', error);
          mostrarAlerta("❌ Error de conexión");
        });
      });
    });
  });

  function mostrarAlerta(mensaje) {
    let cont = document.getElementById('alert-container-global');
    if (!cont) {
        cont = document.createElement('div');
        cont.id = 'alert-container-global';
        Object.assign(cont.style, {
            position: 'fixed', top: '20px', left: '50%', transform: 'translateX(-50%)', zIndex: '3000'
        });
        document.body.appendChild(cont);
    }
    const alerta = document.createElement('div');
    alerta.className = 'alert alert-success shadow';
    alerta.textContent = mensaje;
    Object.assign(alerta.style, { minWidth: '260px', textAlign: 'center', marginTop: '10px' });
    cont.appendChild(alerta);
    setTimeout(() => alerta.remove(), 1800);
  }
});