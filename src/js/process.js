import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export function initProcess(reduced = false) {
  const steps = [...document.querySelectorAll("[data-step]")];
  const bar = document.querySelector("[data-process-bar]");
  const count = document.querySelector("[data-process-count]");

  if (!steps.length) return;

  const setActive = (index) => {
    steps.forEach((step, i) => step.classList.toggle("is-active", i === index));
    if (count) count.textContent = String(index + 1).padStart(2, "0");
  };

  steps.forEach((step, index) => {
    ScrollTrigger.create({
      trigger: step,
      start: "top 58%",
      end: "bottom 58%",
      onToggle: (self) => {
        if (self.isActive) setActive(index);
      },
      onEnterBack: () => setActive(index),
    });
  });

  setActive(0);

  if (!reduced && bar) {
    gsap.fromTo(
      bar,
      { scaleX: 0.16 },
      {
        scaleX: 1,
        ease: "none",
        scrollTrigger: {
          trigger: ".process__steps",
          start: "top 65%",
          end: "bottom 65%",
          scrub: true,
        },
      }
    );
  }
}
