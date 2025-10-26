document.addEventListener('DOMContentLoaded', () => {
    // Solo ejecutar si encontramos el elemento del mini-carrito (para usuarios logueados)
    const miniCartBody = document.querySelector('#lista-carrito tbody');
    if (!miniCartBody) return;

    const totalMinicartSpan = document.getElementById('total-minicart');
    const contadorCarritoSpan = document.getElementById('contador-carrito');

    async function actualizarMiniCarrito() {
        try {
            const response = await fetch('/carrito/datos/');
            const carrito = await response.json();

            // Limpiamos el contenido anterior
            miniCartBody.innerHTML = '';
            let total = 0;
            let cantidadItems = 0;

            if (carrito.length === 0) {
                miniCartBody.innerHTML = '<tr><td colspan="3" class="text-center text-muted small">Tu carrito está vacío</td></tr>';
            } else {
                carrito.forEach(item => {
                    const precioNumerico = parseFloat(item.precio);
                    const subtotalItem = precioNumerico * item.cantidad;
                    total += subtotalItem;
                    cantidadItems += item.cantidad;

                    const fila = document.createElement('tr');
                    fila.innerHTML = `
                        <td><img src="${item.imagen}" width="40" class="rounded"></td>
                        <td class="small">${item.nombre}</td>
                        <td class="small text-end">${item.cantidad} x $${precioNumerico.toLocaleString('es-CL')}</td>
                    `;
                    miniCartBody.appendChild(fila);
                });
            }

            // Actualizamos el total y el contador
            totalMinicartSpan.textContent = `$${total.toLocaleString('es-CL')}`;
            contadorCarritoSpan.textContent = cantidadItems;
            contadorCarritoSpan.style.display = cantidadItems > 0 ? 'inline' : 'none';

        } catch (error) {
            console.error("Error al actualizar el mini-carrito:", error);
        }
    }

    // --- MANEJO DE EVENTOS ---

    // 1. Actualizar al cargar la página
    actualizarMiniCarrito();

    // 2. Escuchar el evento personalizado para actualizar en tiempo real
    window.addEventListener('carritoActualizado', () => {
        console.log('Evento "carritoActualizado" detectado. Actualizando mini-carrito...');
        actualizarMiniCarrito();
    });

    // 3. Botón para vaciar el carrito desde el mini-carrito
    const btnVaciarMinicart = document.getElementById('vaciar-minicart');
    if (btnVaciarMinicart) {
        btnVaciarMinicart.addEventListener('click', async () => {
            await fetch('/carrito/vaciar/', {
                method: 'POST',
                headers: { 'X-CSRFToken': CSRF_TOKEN }
            });
            // Disparamos el evento para que todo se actualice
            window.dispatchEvent(new Event('carritoActualizado'));
        });
    }
});