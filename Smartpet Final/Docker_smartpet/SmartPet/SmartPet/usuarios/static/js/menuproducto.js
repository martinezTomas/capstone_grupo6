// menuproducto.js — versión final con imagen asegurada
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ menuproducto.js cargado correctamente (con imagen garantizada)");

    document.querySelectorAll('.agregar-carrito').forEach(function (btn) {
        btn.addEventListener('click', function (event) {
            event.preventDefault();

            const id = btn.getAttribute('data-id');
            if (!id) {
                console.error("❌ Error: Botón sin data-id.");
                return;
            }

            // ---------------------------------------
            // 1) OBTENER DATOS DEL PRODUCTO
            // ---------------------------------------

            // Prioridad: atributos data-img, data-title, data-desc
            let img = btn.dataset.img || "";
            let title = btn.dataset.title || "";
            let desc = btn.dataset.desc || "";

            // Búsqueda adicional dentro de la tarjeta si falta info
            let productCard = btn.closest('.product');

            if (productCard) {
                if (!img) {
                    const imgEl = productCard.querySelector('img');
                    if (imgEl) img = imgEl.src;
                }
                if (!title) {
                    const titleEl = productCard.querySelector('h3, .card-title, .product-txt h3');
                    if (titleEl) title = titleEl.innerText;
                }
                if (!desc) {
                    const descEl = productCard.querySelector('p, .card-text, .product-txt p:not(.precio)');
                    if (descEl) {
                        desc = descEl.innerText.length > 100
                            ? descEl.innerText.substring(0, 100) + "..."
                            : descEl.innerText;
                    }
                }
            }

            if (!img) img = ""; // Prevención

            // ---------------------------------------
            // 2) ARMAR CONTENIDO DEL MODAL
            // ---------------------------------------

            let modalBody = document.getElementById('modal-body-content');
            if (!modalBody) {
                console.error("❌ modal-body-content no existe en HTML");
                return;
            }

            modalBody.innerHTML = `
                <div class="product-modal-body d-flex flex-column flex-sm-row">
                    <img src="${img}" 
                        class="product-modal-img mb-3 mb-sm-0 me-sm-3"
                        alt="${title}"
                        style="width: 100%; max-width: 120px; height: auto; border-radius: 8px; object-fit: contain;">
                    
                    <div class="product-modal-details flex-grow-1">
                        <h5 class="fw-bold mb-1">${title}</h5>
                        <p class="text-muted mb-3 small">${desc}</p>

                        <div class="product-modal-cantidad d-flex align-items-center gap-2 mt-auto">
                            <label for="cant-${id}" class="form-label small mb-0 me-2">Cantidad:</label>
                            <button type="button" id="menos-${id}" class="btn btn-outline-secondary btn-sm py-0 px-2">−</button>
                            
                            <input type="number" id="cant-${id}" 
                                class="form-control form-control-sm text-center"
                                min="1" value="1" style="width: 60px;">
                            
                            <button type="button" id="mas-${id}" class="btn btn-outline-secondary btn-sm py-0 px-2">+</button>
                        </div>
                    </div>
                </div>
            `;

            // ---------------------------------------
            // 3) LÓGICA DE BOTONES DE CANTIDAD
            // ---------------------------------------

            const inputCant = document.getElementById(`cant-${id}`);
            const btnMenos = document.getElementById(`menos-${id}`);
            const btnMas = document.getElementById(`mas-${id}`);

            btnMenos.onclick = () => {
                let val = Number(inputCant.value);
                if (val > 1) inputCant.value = val - 1;
            };

            btnMas.onclick = () => {
                let val = Number(inputCant.value);
                inputCant.value = val + 1;
            };

            // ---------------------------------------
            // 4) ABRIR MODAL
            // ---------------------------------------

            const modalEl = document.getElementById('productoModal');
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
            modal.show();

            // ---------------------------------------
            // 5) EVENTO BOTÓN "AÑADIR AL CARRITO"
            // ---------------------------------------

            const btnAddModalOriginal = modalEl.querySelector('.btn-add-to-cart-modal');
            const btnAddModal = btnAddModalOriginal.cloneNode(true);
            btnAddModalOriginal.parentNode.replaceChild(btnAddModal, btnAddModalOriginal);

            btnAddModal.addEventListener('click', () => {
                const cantidad = Number(inputCant.value);

                if (isNaN(cantidad) || cantidad < 1) {
                    alert("Ingrese una cantidad válida.");
                    return;
                }

                btnAddModal.disabled = true;
                btnAddModal.textContent = "Añadiendo...";

                fetch('/api/carrito/agregar/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': CSRF_TOKEN
                    },
                    body: JSON.stringify({ id, cantidad })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        window.dispatchEvent(new Event("carritoActualizado"));
                        modal.hide();
                        mostrarAlerta("Producto añadido al carrito", "success");
                    } else {
                        mostrarAlerta("Error: " + data.message, "danger");
                    }
                })
                .catch(err => {
                    mostrarAlerta("Error de conexión", "danger");
                    console.error(err);
                })
                .finally(() => {
                    btnAddModal.disabled = false;
                    btnAddModal.textContent = "Añadir al carrito";
                });
            });

        });
    });

    // ---------------------------------------
    // 7) SISTEMA DE ALERTAS
    // ---------------------------------------
    function mostrarAlerta(msg, tipo) {
        let cont = document.getElementById('alert-container-global');
        if (!cont) {
            cont = document.createElement('div');
            cont.id = 'alert-container-global';
            cont.style.position = "fixed";
            cont.style.top = "70px";
            cont.style.left = "50%";
            cont.style.transform = "translateX(-50%)";
            cont.style.zIndex = "3000";
            document.body.appendChild(cont);
        }

        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-dismissible fade show shadow-sm`;
        alerta.innerHTML = `
            ${msg}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        cont.appendChild(alerta);

        setTimeout(() => {
            alerta.remove();
        }, 2500);
    }

});
