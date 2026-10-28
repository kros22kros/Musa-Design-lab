import { site } from "../data/site.js";

/**
 * Formulario sin backend: valida y abre el correo del usuario con el
 * mensaje preparado. Si más adelante se conecta un servicio (Formspree,
 * Resend, etc.) solo hay que sustituir este bloque.
 */
export function initForm() {
  const form = document.querySelector("[data-form]");
  if (!form) return;

  const status = form.querySelector("[data-form-status]");
  const submit = form.querySelector('button[type="submit"]');

  const setStatus = (message, type) => {
    if (!status) return;
    status.textContent = message;
    status.classList.remove("is-success", "is-error");
    if (type) status.classList.add(type);
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!form.checkValidity()) {
      setStatus("Revisa los campos marcados para poder continuar.", "is-error");
      form.reportValidity();
      return;
    }

    const data = Object.fromEntries(new FormData(form).entries());
    const subject = `Nuevo proyecto — ${data.empresa || data.nombre}`;
    const body = [
      `Nombre: ${data.nombre}`,
      `Empresa: ${data.empresa || "—"}`,
      `Correo: ${data.email}`,
      `Servicio de interés: ${data.servicio || "—"}`,
      "",
      "Mensaje:",
      data.mensaje,
    ].join("\n");

    const mailto = `mailto:${site.email}?subject=${encodeURIComponent(
      subject
    )}&body=${encodeURIComponent(body)}`;

    window.location.href = mailto;

    setStatus(
      `Abrimos tu gestor de correo con el mensaje listo. Si no se abrió, escríbenos a ${site.email}.`,
      "is-success"
    );

    if (submit) {
      const label = submit.querySelector("span");
      if (label) {
        const original = label.textContent;
        label.textContent = "Mensaje preparado";
        window.setTimeout(() => {
          label.textContent = original;
        }, 3200);
      }
    }
  });

  form.querySelectorAll("input, textarea, select").forEach((field) => {
    field.addEventListener("input", () => {
      if (status?.classList.contains("is-error")) {
        setStatus("Este formulario abre tu correo con el mensaje listo para enviar.", null);
      }
    });
  });
}
