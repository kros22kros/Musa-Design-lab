import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import SplitType from "split-type";

gsap.registerPlugin(ScrollTrigger);

let splits = [];
let splitTriggers = [];
let lastWidth = window.innerWidth;

function buildSplitHeadings() {
  splitTriggers.forEach((trigger) => trigger.kill());
  splitTriggers = [];
  splits.forEach((split) => split.revert());
  splits = [];

  document.querySelectorAll("[data-split]").forEach((el) => {
    const split = new SplitType(el, {
      types: "lines",
      lineClass: "split-src",
      autoSplit: false,
    });

    splits.push(split);

    split.lines.forEach((line) => {
      const mask = document.createElement("span");
      mask.className = "split-line";
      line.parentNode.insertBefore(mask, line);
      mask.appendChild(line);
    });

    gsap.set(split.lines, { yPercent: 110 });

    const tween = gsap.to(split.lines, {
      yPercent: 0,
      duration: 1.25,
      stagger: 0.08,
      ease: "expo.out",
      scrollTrigger: {
        trigger: el,
        start: "top 87%",
        once: true,
      },
    });

    splitTriggers.push(tween.scrollTrigger);
  });
}

/**
 * Apariciones, titulares partidos por líneas, parallax y contadores.
 */
export function initReveals(reduced = false) {
  if (reduced) {
    gsap.set("[data-reveal]", { opacity: 1, y: 0 });
    gsap.set("[data-image-reveal]", { clipPath: "inset(0 0 0% 0)" });
    return;
  }

  document.querySelectorAll("[data-reveal]").forEach((el) => {
    gsap.to(el, {
      opacity: 1,
      y: 0,
      duration: 1.05,
      ease: "power3.out",
      scrollTrigger: {
        trigger: el,
        start: "top 88%",
        once: true,
      },
    });
  });

  document.querySelectorAll("[data-image-reveal]").forEach((el) => {
    gsap.to(el, {
      clipPath: "inset(0 0 0% 0)",
      duration: 1.5,
      ease: "expo.out",
      scrollTrigger: {
        trigger: el,
        start: "top 86%",
        once: true,
      },
    });
  });

  document.querySelectorAll("[data-parallax]").forEach((el) => {
    gsap.fromTo(
      el,
      { yPercent: -4, scale: 1.08 },
      {
        yPercent: 4,
        scale: 1.03,
        ease: "none",
        scrollTrigger: {
          trigger: el.closest("[data-parallax-wrap]") || el,
          start: "top bottom",
          end: "bottom top",
          scrub: true,
        },
      }
    );
  });

  document.querySelectorAll("[data-count]").forEach((el) => {
    const target = Number(el.dataset.count);
    const pad = Number(el.dataset.pad || 2);
    const state = { value: 0 };

    gsap.to(state, {
      value: target,
      duration: 1.5,
      ease: "power2.out",
      scrollTrigger: {
        trigger: el,
        start: "top 92%",
        once: true,
      },
      onUpdate: () => {
        el.textContent = String(Math.round(state.value)).padStart(pad, "0");
      },
    });
  });

  buildSplitHeadings();

  window.addEventListener("resize", () => {
    if (Math.abs(window.innerWidth - lastWidth) < 60) return;
    lastWidth = window.innerWidth;
    window.clearTimeout(window.__musaSplitTimer);
    window.__musaSplitTimer = window.setTimeout(() => {
      buildSplitHeadings();
      ScrollTrigger.refresh();
    }, 280);
  });
}

/**
 * Interfaz ligada al scroll: barra de progreso, estado de la nav,
 * enlace activo y velocidad del marquee.
 */
export function initScrollUI() {
  const nav = document.querySelector("#nav");
  const marquee = document.querySelector("[data-marquee-track]");

  let marqueeTween = null;
  if (marquee) {
    marqueeTween = gsap.to(marquee, {
      xPercent: -50,
      duration: 30,
      repeat: -1,
      ease: "none",
    });
  }

  ScrollTrigger.create({
    start: 0,
    end: "max",
    onUpdate: (self) => {
      nav?.classList.toggle("is-scrolled", self.scroll() > 90);

      if (marqueeTween) {
        const boost = Math.min(2.6, Math.abs(self.getVelocity()) / 1200);
        gsap.to(marqueeTween, {
          timeScale: 1 + boost,
          duration: 0.6,
          overwrite: true,
        });
      }
    },
  });

  // Enlace activo en la navegación
  const links = [...document.querySelectorAll("[data-nav-link]")];
  const sections = links
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);

  if (!sections.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        links.forEach((link) => {
          link.classList.toggle(
            "is-active",
            link.getAttribute("href") === `#${entry.target.id}`
          );
        });
      });
    },
    { rootMargin: "-40% 0px -55% 0px", threshold: 0 }
  );

  sections.forEach((section) => observer.observe(section));
}
