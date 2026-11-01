import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/**
 * Entrada del hero. Devuelve una timeline pausada que se reproduce
 * cuando el preloader empieza a retirarse.
 */
export function createHeroIntro(reduced = false) {
  const hero = document.querySelector(".hero");
  if (!hero) return null;

  if (reduced) return gsap.timeline({ paused: true });

  const lines = hero.querySelectorAll(".hero__title .line__inner");
  const eyebrow = hero.querySelector(".hero__eyebrow");
  const lead = hero.querySelector(".hero__lead");
  const buttons = hero.querySelectorAll(".hero__actions .btn");
  const foot = hero.querySelectorAll(".hero__foot-item, .hero__scroll");

  gsap.set(lines, { yPercent: 112 });
  gsap.set([eyebrow, lead, buttons, foot], { opacity: 0, y: 18 });

  const tl = gsap.timeline({
    paused: true,
    defaults: { ease: "expo.out" },
  });

  tl.to(eyebrow, { opacity: 1, y: 0, duration: 1 }, 0)
    .to(
      lines,
      { yPercent: 0, duration: 1.35, stagger: 0.11 },
      0.08
    )
    .to(lead, { opacity: 1, y: 0, duration: 1.1 }, 0.55)
    .to(
      buttons,
      { opacity: 1, y: 0, duration: 1, stagger: 0.1 },
      0.7
    )
    .to(
      foot,
      { opacity: 1, y: 0, duration: 0.9, stagger: 0.08 },
      0.85
    );

  return tl;
}

/** Pausa la animación ambiental del hero cuando deja de verse. */
export function initHeroAmbience(reduced = false) {
  const hero = document.querySelector(".hero");
  if (!hero || reduced || !("IntersectionObserver" in window)) return;

  const io = new IntersectionObserver(
    ([entry]) => {
      hero.classList.toggle("is-idle", !entry.isIntersecting);
    },
    { rootMargin: "10%" }
  );

  io.observe(hero);
}

/**
 * Profundidad con el puntero: las tarjetas flotantes se desplazan a
 * distintas velocidades según su capa. Solo con mouse o trackpad.
 */
export function initHeroDepth(reduced = false) {
  const hero = document.querySelector(".hero");
  if (!hero || reduced) return;
  if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;

  const target = { x: 0, y: 0 };
  const current = { x: 0, y: 0 };
  let frame = 0;

  const tick = () => {
    current.x += (target.x - current.x) * 0.055;
    current.y += (target.y - current.y) * 0.055;

    hero.style.setProperty("--mx", current.x.toFixed(4));
    hero.style.setProperty("--my", current.y.toFixed(4));

    const pending =
      Math.abs(target.x - current.x) + Math.abs(target.y - current.y) > 0.0008;
    frame = pending ? requestAnimationFrame(tick) : 0;
  };

  const onMove = (event) => {
    target.x = (event.clientX / window.innerWidth - 0.5) * 2;
    target.y = (event.clientY / window.innerHeight - 0.5) * 2;
    if (!frame) frame = requestAnimationFrame(tick);
  };

  hero.style.setProperty("--mx", "0");
  hero.style.setProperty("--my", "0");
  window.addEventListener("pointermove", onMove, { passive: true });
}

/** Parallax del video y del contenido del hero al hacer scroll. */
export function initHeroParallax(reduced = false) {
  const hero = document.querySelector(".hero");
  if (!hero || reduced) return;

  gsap.to(".hero__inner", {
    yPercent: -6,
    opacity: 0.35,
    ease: "none",
    scrollTrigger: {
      trigger: hero,
      start: "top top",
      end: "bottom top",
      scrub: true,
    },
  });

  gsap.to(".hero__halo", {
    rotate: 40,
    yPercent: 8,
    ease: "none",
    scrollTrigger: {
      trigger: hero,
      start: "top top",
      end: "bottom top",
      scrub: true,
    },
  });

  gsap.to(".hero__cards", {
    y: -70,
    opacity: 0.35,
    ease: "none",
    scrollTrigger: {
      trigger: hero,
      start: "top top",
      end: "bottom top",
      scrub: true,
    },
  });
}
