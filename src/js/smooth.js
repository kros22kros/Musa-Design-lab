import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";

gsap.registerPlugin(ScrollTrigger);

/**
 * Scroll suave con Lenis sincronizado a GSAP ScrollTrigger.
 * En modo reducido devuelve null y se usa el scroll nativo.
 */
export function createSmoothScroll(reduced = false) {
  if (reduced) {
    return {
      lenis: null,
      scrollTo(target) {
        const el = typeof target === "string" ? document.querySelector(target) : target;
        if (el) el.scrollIntoView({ behavior: "auto", block: "start" });
      },
    };
  }

  const lenis = new Lenis({
    duration: 1.15,
    smoothWheel: true,
    wheelMultiplier: 0.95,
    touchMultiplier: 1.4,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  });

  lenis.on("scroll", ScrollTrigger.update);

  gsap.ticker.add((time) => {
    lenis.raf(time * 1000);
  });
  gsap.ticker.lagSmoothing(0);

  const scrollTo = (target) => {
    const el = typeof target === "string" ? document.querySelector(target) : target;
    if (!el) return;
    lenis.scrollTo(el, { offset: -8, duration: 1.4 });
  };

  return { lenis, scrollTo };
}

/** Enlaza todos los anclajes internos al scroll suave. */
export function bindAnchors(scrollTo, onNavigate) {
  document.addEventListener("click", (event) => {
    const link = event.target.closest('a[href^="#"]');
    if (!link) return;

    const hash = link.getAttribute("href");
    if (!hash || hash === "#") return;

    const target = document.querySelector(hash);
    if (!target) return;

    event.preventDefault();
    onNavigate?.(link);
    scrollTo(target);
    history.pushState(null, "", hash);
  });
}
