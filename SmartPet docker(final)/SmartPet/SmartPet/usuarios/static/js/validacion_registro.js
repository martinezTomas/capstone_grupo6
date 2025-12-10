document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("registerForm");

  // Inputs
  const iUsername = document.getElementById("id_username");
  const iFirst = document.getElementById("id_first_name");
  const iLast = document.getElementById("id_last_name");
  const iEmail = document.getElementById("id_email");
  const iPass1 = document.getElementById("id_password1");
  const iPass2 = document.getElementById("id_password2");

  // Regex
  const nameRegex = /^[A-Za-zÁÉÍÓÚÑáéíóúñ\s]{2,}$/;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const passRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

  function setState(input, ok, message = "") {
    let feedback = input.parentElement.querySelector(".invalid-feedback");
    if (!feedback) {
      feedback = document.createElement("div");
      feedback.className = "invalid-feedback";
      input.parentElement.appendChild(feedback);
    }

    if (ok) {
      input.classList.remove("is-invalid");
      input.classList.add("is-valid");
      feedback.textContent = "";
    } else {
      input.classList.remove("is-valid");
      input.classList.add("is-invalid");
      feedback.textContent = message;
    }
  }

  function validateUsername() {
    const v = iUsername.value.trim();
    if (v.length < 4) {
      setState(iUsername, false, "Debe tener al menos 4 caracteres.");
      return false;
    }
    setState(iUsername, true);
    return true;
  }

  function validateFirst() {
    const v = iFirst.value.trim();
    if (!nameRegex.test(v)) {
      setState(iFirst, false, "Solo letras y espacios. Mínimo 2 caracteres.");
      return false;
    }
    setState(iFirst, true);
    return true;
  }

  function validateLast() {
    const v = iLast.value.trim();
    if (!nameRegex.test(v)) {
      setState(iLast, false, "Solo letras y espacios. Mínimo 2 caracteres.");
      return false;
    }
    setState(iLast, true);
    return true;
  }

  function validateEmail() {
    const v = iEmail.value.trim();
    if (!emailRegex.test(v)) {
      setState(iEmail, false, "Ingresa un correo válido (ej. nombre@dominio.com).");
      return false;
    }
    setState(iEmail, true);
    return true;
  }

  function validatePass1() {
    const v = iPass1.value;
    if (!passRegex.test(v)) {
      setState(iPass1, false, "Min. 8 caracteres con mayúscula, minúscula y número.");
      return false;
    }
    setState(iPass1, true);
    return true;
  }

  function validatePass2() {
    if (iPass2.value !== iPass1.value || iPass2.value === "") {
      setState(iPass2, false, "Las contraseñas no coinciden.");
      return false;
    }
    setState(iPass2, true);
    return true;
  }

  // Eventos de validación en tiempo real
  iUsername.addEventListener("input", validateUsername);
  iFirst.addEventListener("input", validateFirst);
  iLast.addEventListener("input", validateLast);
  iEmail.addEventListener("input", validateEmail);
  iPass1.addEventListener("input", () => {
    validatePass1();
    validatePass2();
  });
  iPass2.addEventListener("input", validatePass2);

  // Validación al enviar
  form.addEventListener("submit", function (e) {
    const ok =
      validateUsername() &
      validateFirst() &
      validateLast() &
      validateEmail() &
      validatePass1() &
      validatePass2();

    if (!ok) {
      e.preventDefault();
      e.stopPropagation();
      const firstInvalid = form.querySelector(".is-invalid");
      if (firstInvalid)
        firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });
});
