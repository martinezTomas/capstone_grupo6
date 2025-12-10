// static/js/login_validation.js

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("loginForm");
    if (!form) return; // No hacer nada si no estamos en la página de login

    const iUsername = document.getElementById("id_username");
    const iPassword = document.getElementById("id_password");

    // Función simple para mostrar/ocultar errores (como en tu register.js)
    function setState(input, ok, message = "") {
        let feedback = input.parentElement.querySelector(".invalid-feedback");
        if (!feedback) {
            feedback = document.createElement("div");
            feedback.className = "invalid-feedback";
            // Insertar después del input-group, no dentro
            input.parentElement.parentNode.appendChild(feedback);
        }

        if (ok) {
            input.classList.remove("is-invalid");
            input.classList.add("is-valid");
            feedback.textContent = "";
            feedback.classList.remove("d-block"); // Ocultar
        } else {
            input.classList.remove("is-valid");
            input.classList.add("is-invalid");
            feedback.textContent = message;
            feedback.classList.add("d-block"); // Mostrar
        }
    }

    // --- Funciones de Validación ---
    function validateUsername() {
        if (iUsername.value.trim() === "") {
            setState(iUsername, false, "Por favor, ingresa tu nombre de usuario.");
            return false;
        }
        setState(iUsername, true);
        return true;
    }

    function validatePassword() {
        if (iPassword.value.trim() === "") {
            setState(iPassword, false, "Por favor, ingresa tu contraseña.");
            return false;
        }
        setState(iPassword, true);
        return true;
    }

    // --- Eventos ---
    iUsername.addEventListener("input", validateUsername);
    iPassword.addEventListener("input", validatePassword);

    // --- Validación al Enviar ---
    form.addEventListener("submit", function (e) {
        // (Usamos el operador & para que se ejecuten todas las validaciones)
        const ok = validateUsername() & validatePassword();

        if (!ok) {
            e.preventDefault(); // Detener el envío del formulario
            e.stopPropagation();
            
            // Hacer foco en el primer error
            const firstInvalid = form.querySelector(".is-invalid");
            if (firstInvalid) {
                firstInvalid.focus();
            }
        }
    });
});