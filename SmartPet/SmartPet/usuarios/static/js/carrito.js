document.addEventListener("DOMContentLoaded", function () {
    const carritoBody = document.getElementById("carrito-body");

    // ✅ Condición de seguridad: Si no estamos en la página del carrito (es decir,
    // si no se encuentra el elemento 'carrito-body'), el script se detiene aquí
    // y no intentará ejecutar el resto del código, evitando el error.
    if (!carritoBody) {
        return; 
    }

    // Si el script llega hasta aquí, significa que estamos en la página correcta.
    console.log("✅ carrito.js (versión DB) cargado correctamente en la página del carrito.");

    const totalSpan = document.getElementById("total");
    const subtotalSpan = document.getElementById("subtotal");
    const envioSpan = document.getElementById("envio");
    const btnVaciar = document.getElementById("vaciar-carrito");

    // 👉 Muestra los productos pidiéndolos a la base de datos de Django
    function mostrarCarrito() {
        fetch("/carrito/datos/") 
          .then((response) => response.json())
          .then((carrito) => {
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
                fila.innerHTML = `
                  <td><img src="${prod.imagen}" width="60" height="60" style="border-radius:8px"></td>
                  <td>${prod.nombre}</td>
                  <td class="text-center">
                    <div class="d-flex align-items-center justify-content-center gap-2">
                      <button class="btn btn-outline-secondary btn-sm btn-restar" data-id="${prod.id}">−</button>
                      <span class="fw-bold">${cantidad}</span>
                      <button class="btn btn-outline-secondary btn-sm btn-sumar" data-id="${prod.id}">+</button>
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

            const envio = subtotal >= 30000 ? 0 : 2990;
            const total = subtotal + envio;
            subtotalSpan.textContent = `$${subtotal.toLocaleString("es-CL")}`;
            envioSpan.textContent =
              envio === 0 ? "🚚 ¡Gratis!" : `$${envio.toLocaleString("es-CL")}`;
            totalSpan.textContent = `$${total.toLocaleString("es-CL")}`;
          });
    }

    // 👉 Función genérica para enviar actualizaciones a Django
    function actualizarServidor(url, body) {
        return fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CSRF_TOKEN,
            },
            body: JSON.stringify(body),
        }).then((response) => response.json());
    }

    // 👉 Escuchar eventos de los botones (+, −, Eliminar)
    carritoBody.addEventListener("click", function (e) {
        const id = e.target.dataset.id;
        if (!id) return;

        if (e.target.matches(".btn-sumar, .btn-restar")) {
            const accion = e.target.classList.contains("btn-sumar") ? "sumar" : "restar";
            actualizarServidor("/carrito/actualizar/", { id, accion }).then((data) => {
                if (data.status === "success") {
                    mostrarCarrito();
                    window.dispatchEvent(new Event("carritoActualizado"));
                }
            });
        }

        if (e.target.matches(".btn-eliminar")) {
            actualizarServidor("/carrito/eliminar/", { id }).then((data) => {
                if (data.status === "success") {
                    mostrarCarrito();
                    window.dispatchEvent(new Event("carritoActualizado"));
                }
            });
        }
    });

    // 👉 Vaciar carrito completo
    if (btnVaciar) {
        btnVaciar.addEventListener("click", () => {
            actualizarServidor("/carrito/vaciar/", {}).then((data) => {
                if (data.status === "success") {
                    mostrarCarrito();
                    window.dispatchEvent(new Event("carritoActualizado"));
                }
            });
        });
    }

    // 👉 Mostrar el carrito en cuanto se carga la página
    mostrarCarrito();
});