// static/js/minicart.js (COMPLETO Y CORREGIDO)

document.addEventListener('DOMContentLoaded', () => {
    // Solo ejecutar si encontramos el cuerpo de la tabla del mini-carrito
    const miniCartBody = document.querySelector('#lista-carrito tbody');
    if (!miniCartBody) return; // Si no existe, este script no hace nada

    console.log("✅ minicart.js cargado correctamente.");

    // Elementos donde mostraremos la información
    const totalMinicartSpan = document.getElementById('total-minicart');
    const contadorCarritoSpan = document.getElementById('contador-carrito');

    // Función asíncrona para obtener datos y actualizar el HTML
    async function actualizarMiniCarrito() {
        try {
            // 
            // ✅ CORRECCIÓN 1: URL cambiada de '/carrito/datos/' a '/api/carrito/ver/'
            // 
            const response = await fetch('/api/carrito/ver/'); // <-- URL CORREGIDA

            // Verificar si la respuesta de red fue exitosa
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status} ${response.statusText}`);
            }
            const carrito = await response.json(); // Convertir respuesta a JSON

            // Limpiamos el contenido anterior
            miniCartBody.innerHTML = '';
            let total = 0;
            let cantidadItems = 0;

            if (carrito.length === 0) {
                // ✅ Mensaje de carrito vacío (COMPLETO)
                miniCartBody.innerHTML = '<tr><td colspan="3" class="text-center text-muted small py-2">Tu carrito está vacío</td></tr>';
            } else {
                // ✅ Lógica para crear filas (COMPLETO)
                carrito.forEach(item => {
                    const precioNumerico = parseFloat(item.precio);
                    // Validar que cantidad sea un número antes de sumar
                    const cantidadItem = parseInt(item.cantidad, 10) || 0; 
                    const subtotalItem = precioNumerico * cantidadItem;
                    total += subtotalItem;
                    cantidadItems += cantidadItem;

                    const fila = document.createElement('tr');
                    // Añadimos clases para mejor estilo si es necesario
                    fila.classList.add('minicart-item'); 
                    fila.innerHTML = `
                        <td class="py-1 px-1 align-middle">
                            <img src="${item.imagen}" alt="${item.nombre}" width="40" height="40" class="rounded" style="object-fit: cover;">
                        </td>
                        <td class="small py-1 px-1 align-middle" style="white-space: normal;">
                            ${item.nombre} ${item.peso ? '<span class="text-muted">('+item.peso+')</span>' : ''}
                        </td>
                        <td class="small py-1 px-1 align-middle text-end">
                            ${cantidadItem}&nbsp;x&nbsp;$${precioNumerico.toLocaleString('es-CL')}
                        </td>
                    `;
                    miniCartBody.appendChild(fila);
                });
            }

            // ✅ Lógica para actualizar totales (COMPLETO)
            if (totalMinicartSpan) {
                totalMinicartSpan.textContent = `$${total.toLocaleString('es-CL')}`;
            }
            if (contadorCarritoSpan) {
                contadorCarritoSpan.textContent = cantidadItems;
                // Mostrar/ocultar el contador si hay items o no
                contadorCarritoSpan.style.display = cantidadItems > 0 ? 'inline-block' : 'none'; 
            }

        } catch (error) {
            console.error("Error al actualizar el mini-carrito:", error);
            // ✅ Mensaje de error (COMPLETO)
            miniCartBody.innerHTML = '<tr><td colspan="3" class="text-center text-danger small py-2">Error al cargar</td></tr>';
            if (contadorCarritoSpan) contadorCarritoSpan.style.display = 'none'; // Ocultar contador en caso de error
        }
    }

    // --- MANEJO DE EVENTOS ---

    // 1. Actualizar al cargar la página inicialmente
    actualizarMiniCarrito();

    // 2. Escuchar el evento personalizado 'carritoActualizado'
    // Este evento debe ser disparado por otros scripts (menuproducto.js, carrito.js)
    // cuando modifican el carrito.
    window.addEventListener('carritoActualizado', () => {
        console.log('Evento "carritoActualizado" detectado. Actualizando mini-carrito...');
        actualizarMiniCarrito();
    });

    // 3. Botón para vaciar el carrito desde el mini-carrito
    const btnVaciarMinicart = document.getElementById('vaciar-minicart');
    if (btnVaciarMinicart) {
        btnVaciarMinicart.addEventListener('click', async () => {
            // (Opcional: Pedir confirmación)
            if (!confirm("¿Seguro que quieres vaciar el carrito?")) return;

            try {
                // Asegúrate de que CSRF_TOKEN esté definido
                if (typeof CSRF_TOKEN === 'undefined') { throw new Error("CSRF_TOKEN no definido"); }

                // 
                // ✅ CORRECCIÓN 2: URL cambiada a '/api/carrito/vaciar/'
                // 
                const response = await fetch('/api/carrito/vaciar/', { // <-- URL CORREGIDA
                    method: 'POST',
                    headers: { 
                        'X-CSRFToken': CSRF_TOKEN,
                        'Content-Type': 'application/json' // Aunque no enviemos body, es buena práctica
                    } 
                    // No necesita body para vaciar
                });

                if (!response.ok) { throw new Error(`Error HTTP: ${response.status}`); }
                
                // Disparamos el evento para que todo se actualice (incluido este mismo minicart)
                window.dispatchEvent(new Event('carritoActualizado'));

            } catch (error) {
                console.error("Error al vaciar el mini-carrito:", error);
                alert("Error de conexión al intentar vaciar el carrito.");
            }
        });
    }
}); // Fin del DOMContentLoaded