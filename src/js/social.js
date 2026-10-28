import { site } from "../data/site.js";

/**
 * Aplica correo, redes y año en todos los puntos del sitio.
 */
export function applySiteConfig() {
  document.querySelectorAll("[data-email]").forEach((link) => {
    link.href = `mailto:${site.email}`;
    link.textContent = site.email;
  });

  document.querySelectorAll("[data-social]").forEach((link) => {
    const url = site.social[link.dataset.social];
    if (!url) return;
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  });

  document.querySelectorAll("[data-year]").forEach((el) => {
    el.textContent = String(new Date().getFullYear());
  });
}
