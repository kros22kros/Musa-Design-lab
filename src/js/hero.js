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

/** Parallax del video y del contenido del hero al hacer scroll. */
export function initHeroParallax(reduced = false) {
  const hero = document.querySelector(".hero");
  if (!hero || reduced) return;

  gsap.to(".hero__video", {
    yPercent: 12,
    scale: 1.14,
    ease: "none",
    scrollTrigger: {
      trigger: hero,
      start: "top top",
      end: "bottom top",
      scrub: true,
    },
  });

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
}
