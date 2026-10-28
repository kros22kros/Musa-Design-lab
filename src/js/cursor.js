import gsap from "gsap";

/**
 * Cursor personalizado con mezcla de diferencia y etiqueta contextual.
 * Solo se activa en dispositivos con puntero fino y sin movimiento reducido.
 */
export function initCursor(reduced = false) {
  const root = document.documentElement;
  const cursor = document.querySelector(".cursor");
  const dot = cursor?.querySelector(".cursor__dot");
  const ring = cursor?.querySelector(".cursor__ring");
  const label = cursor?.querySelector(".cursor__label");

  if (!cursor || reduced || !window.matchMedia("(pointer: fine)").matches) return;

  root.classList.add("has-cursor");
  gsap.set([dot, ring], { xPercent: -50, yPercent: -50 });

  const dotX = gsap.quickTo(dot, "x", { duration: 0.12, ease: "power2.out" });
  const dotY = gsap.quickTo(dot, "y", { duration: 0.12, ease: "power2.out" });
  const ringX = gsap.quickTo(ring, "x", { duration: 0.45, ease: "power3.out" });
  const ringY = gsap.quickTo(ring, "y", { duration: 0.45, ease: "power3.out" });

  let visible = false;

  window.addEventListener(
    "mousemove",
    (event) => {
      if (!visible) {
        visible = true;
        gsap.to(cursor, { opacity: 1, duration: 0.3 });
        gsap.set([dot, ring], { x: event.clientX, y: event.clientY });
      }
      dotX(event.clientX);
      dotY(event.clientY);
      ringX(event.clientX);
      ringY(event.clientY);
    },
    { passive: true }
  );

  document.addEventListener("mouseleave", () => {
    visible = false;
    gsap.to(cursor, { opacity: 0, duration: 0.25 });
  });

  document.addEventListener("mouseover", (event) => {
    const target = event.target.closest(
      "a, button, [data-cursor], [data-lightbox], input, textarea, select"
    );

    if (!target) return;

    const text = target.getAttribute("data-cursor");
    if (text) {
      label.textContent = text;
      cursor.classList.add("is-label");
      cursor.classList.remove("is-hover");
      return;
    }

    if (target.matches("[data-lightbox]")) {
      label.textContent = "Ver";
      cursor.classList.add("is-label");
      cursor.classList.remove("is-hover");
      return;
    }

    cursor.classList.remove("is-label");
    cursor.classList.add("is-hover");
  });

  document.addEventListener("mouseout", (event) => {
    const from = event.target.closest(
      "a, button, [data-cursor], [data-lightbox], input, textarea, select"
    );
    if (!from) return;
    const to = event.relatedTarget?.closest?.(
      "a, button, [data-cursor], [data-lightbox], input, textarea, select"
    );
    if (to === from) return;

    cursor.classList.remove("is-hover", "is-label");
  });
}
