/**
 * Configuración editable del sitio.
 * Datos de contacto reales de MUSA Design Lab.
 */
export const site = {
  name: "MUSA Design Lab",
  city: "Sogamoso, Boyacá",
  instagram: {
    handle: "musa_designlab",
    url: "https://www.instagram.com/musa_designlab",
  },
  whatsapp: [
    { number: "573213827782", display: "+57 321 382 7782" },
    { number: "573214179741", display: "+57 321 417 9741" },
    { number: "573227497053", display: "+57 322 749 7053" },
  ],
};

/** Enlace de WhatsApp con mensaje opcional. */
export function whatsappLink(text = "", number = site.whatsapp[0].number) {
  const base = `https://wa.me/${number}`;
  return text ? `${base}?text=${encodeURIComponent(text)}` : base;
}
