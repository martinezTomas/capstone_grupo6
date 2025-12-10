// static/js/carrito.js (SIN CONFIRMACIONES, FUNCIONAL)

document.addEventListener("DOMContentLoaded", function () {
    const carritoBody = document.getElementById("carrito-body");

    if (!carritoBody) return;

    console.log("✅ carrito.js cargado correctamente en la página del carrito.");

    const totalSpan = document.getElementById("total");
    const subtotalSpan = document.getElementById("subtotal");
    const envioSpan = document.getElementById("envio");
    const btnVaciar = document.getElementById("vaciar-carrito");

    // --- Mostrar productos del carrito ---
    function mostrarCarrito() {
        fetch('/api/carrito/ver/')
          .then(response => {
            if (!response.ok) throw new Error(`Error HTTP ${response.status}: ${response.statusText}`);
            return response.json();
          })
          .then(carrito => {
            carritoBody.innerHTML = "";
            let subtotal = 0;

            if (carrito.length === 0) {
                carritoBody.innerHTML = `
                <tr>
                  <td colspan="6" class="text-center text-muted py-4">
                    🛒 Tu carrito está vacío
                  </td>
                </tr>`;
            } else {
                carrito.forEach((prod) => {
                    const precioNumerico = parseFloat(prod.precio);
                    const cantidad = parseInt(prod.cantidad, 10);
                    const subtotalProducto = precioNumerico * cantidad;
                    subtotal += subtotalProducto;

                    const fila = document.createElement("tr");
                    fila.setAttribute('id', `item-carrito-${prod.id}`);
                    fila.innerHTML = `
                      <td><img src="${prod.imagen}" alt="${prod.nombre}" width="60" height="60" style="border-radius:8px; object-fit: cover;"></td>
                      <td>${prod.nombre} ${prod.peso ? '('+prod.peso+')' : ''}</td> 
                      <td class="text-center">
                        <div class="d-flex align-items-center justify-content-center gap-2">
                          <button class="btn btn-outline-secondary btn-sm btn-restar" data-id="${prod.id}" aria-label="Restar uno">−</button>
                          <span class="fw-bold px-2" style="min-width: 25px;">${cantidad}</span>
                          <button class="btn btn-outline-secondary btn-sm btn-sumar" data-id="${prod.id}" aria-label="Sumar uno">+</button>
                        </div>
                      </td>
                      <td class="text-center">$${precioNumerico.toLocaleString("es-CL")}</td>
                      <td class="text-center">$${subtotalProducto.toLocaleString("es-CL")}</td>
                      <td class="text-center">
                        <button class="btn btn-outline-danger btn-sm btn-eliminar" data-id="${prod.id}">Eliminar</button>
                      </td>`;
                    carritoBody.appendChild(fila);
                });
            }

            // Calcular totales
            const envio = 0; // El envío NO se calcula en esta página
            const total = subtotal; // El total es igual al subtotal

            if (subtotalSpan) subtotalSpan.textContent = `$${subtotal.toLocaleString("es-CL")}`;
            if (envioSpan) envioSpan.textContent = "Por calcular"; // <-- ✅ CORREGIDO
            if (totalSpan) totalSpan.textContent = `$${total.toLocaleString("es-CL")}`; // <-- ✅ CORREGIDO
          })
          .catch(error => {
            console.error("Error en mostrarCarrito:", error);
            carritoBody.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-4">❌ Error al cargar el carrito. Intenta recargar la página.</td></tr>`;
          });
    }

    // --- Enviar actualizaciones al servidor ---
    function actualizarServidor(url, body) {
        if (typeof CSRF_TOKEN === 'undefined') {
          console.error("Error: CSRF_TOKEN no está definido.");
          alert("Error de seguridad. Recarga la página.");
          return Promise.reject("CSRF_TOKEN missing");
        }
        
        return fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CSRF_TOKEN,
            },
            body: JSON.stringify(body),
        }).then(response => {
            if (!response.ok) throw new Error(`Error ${response.status} en la petición a ${url}`);
            return response.json();
        });
    }

    // --- Delegación de eventos en tabla ---
    carritoBody.addEventListener("click", function (e) {
        const idProducto = e.target.dataset.id;
        if (!idProducto) return;

        // Botones sumar/restar cantidad
        if (e.target.matches(".btn-sumar, .btn-restar")) {
            const accion = e.target.classList.contains("btn-sumar") ? "sumar" : "restar";
            actualizarServidor('/api/carrito/actualizar/', { id: idProducto, accion })
              .then(data => {
                if (data.status === "success") {
                    mostrarCarrito();
                    window.dispatchEvent(new Event("carritoActualizado"));
                } else {
                    console.error("Error al actualizar cantidad:", data.message);
                    alert("Error al actualizar la cantidad.");
                }
              })
              .catch(error => {
                console.error("Error fetch actualizar:", error);
                alert("Error de conexión al actualizar.");
              });
        }

        // Botón eliminar producto — SIN CONFIRMACIÓN
        if (e.target.matches(".btn-eliminar")) {
            actualizarServidor('/api/carrito/eliminar/', { id: idProducto })
              .then(data => {
                if (data.status === "success") {
                    mostrarCarrito();
                    window.dispatchEvent(new Event("carritoActualizado"));
                } else {
                    console.error("Error al eliminar item:", data.message);
                    alert("Error al eliminar el producto.");
                }
              })
              .catch(error => {
                console.error("Error fetch eliminar:", error);
                alert("Error de conexión al eliminar.");
              });
        }
    });

    // --- Botón Vaciar carrito completo — SIN CONFIRMACIÓN ---
    if (btnVaciar) {
        btnVaciar.addEventListener("click", () => {
            actualizarServidor('/api/carrito/vaciar/', {})
              .then(data => {
                if (data.status === "success") {
                    mostrarCarrito();
                    window.dispatchEvent(new Event("carritoActualizado"));
                } else {
                    console.error("Error al vaciar carrito:", data.message);
                    alert("Error al vaciar el carrito.");
                }
              })
              .catch(error => {
                console.error("Error fetch vaciar:", error);
                alert("Error de conexión al vaciar.");
              });
        });
    }

    // --- Cargar el carrito al inicio ---
    mostrarCarrito();
});
