import { site, whatsappLink } from "../data/site.js";

/**
 * Aplica WhatsApp, Instagram, ciudad y año en todos los puntos del sitio.
 */
export function applySiteConfig() {
  document.querySelectorAll("[data-social='instagram']").forEach((link) => {
    link.href = site.instagram.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  });

  document.querySelectorAll("[data-wa]").forEach((link) => {
    const index = Number(link.dataset.wa);
    const contact = site.whatsapp[index] ?? site.whatsapp[0];
    const message = link.dataset.waMessage || "";
    link.href = whatsappLink(message, contact.number);
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    if (!link.textContent.trim()) link.textContent = contact.display;
  });

  document.querySelectorAll("[data-insta-handle]").forEach((el) => {
    el.textContent = `@${site.instagram.handle}`;
  });

  document.querySelectorAll("[data-city]").forEach((el) => {
    el.textContent = site.city;
  });

  document.querySelectorAll("[data-year]").forEach((el) => {
    el.textContent = String(new Date().getFullYear());
  });
}
