import { site, whatsappLink } from "../data/site.js";

/**
 * Formulario sin backend: valida los campos y abre WhatsApp con el
 * mensaje preparado. Si más adelante se conecta un servicio (Formspree,
 * Resend, etc.) solo hay que sustituir este bloque.
 */
export function initForm() {
  const form = document.querySelector("[data-form]");
  if (!form) return;

  const status = form.querySelector("[data-form-status]");
  const submit = form.querySelector('button[type="submit"]');
  const primary = site.whatsapp[0];

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
    const body = [
      `Hola MUSA Design Lab, soy ${data.nombre}.`,
      data.empresa ? `Empresa: ${data.empresa}` : "",
      data.contacto ? `Contacto: ${data.contacto}` : "",
      `Me interesa: ${data.servicio || "asesoría general"}`,
      "",
      data.mensaje,
    ]
      .filter(Boolean)
      .join("\n");

    const url = whatsappLink(body, primary.number);
    const opened = window.open(url, "_blank", "noopener,noreferrer");
    if (!opened) window.location.href = url;

    setStatus(
      `Abrimos WhatsApp con el mensaje listo. Si no se abrió, escríbenos al ${primary.display}.`,
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
        setStatus("Este formulario abre WhatsApp con tu mensaje listo para enviar.", null);
      }
    });
  });
}
