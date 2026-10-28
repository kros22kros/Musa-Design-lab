import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/**
 * Carrusel horizontal de servicios con pin y scrub en escritorio.
 * En pantallas menores funciona como carrusel táctil nativo.
 */
export function initServices(reduced = false) {
  const section = document.querySelector(".services");
  const track = document.querySelector("[data-services-track]");
  const progress = document.querySelector("[data-services-progress]");

  if (!section || !track || reduced) return;

  const setProgress = progress
    ? gsap.quickSetter(progress, "scaleX")
    : () => {};

  const mm = gsap.matchMedia();

  mm.add("(min-width: 1025px)", () => {
    const distance = () =>
      Math.max(0, track.scrollWidth - window.innerWidth + 8);

    const tween = gsap.to(track, {
      x: () => -distance(),
      ease: "none",
      scrollTrigger: {
        trigger: section,
        start: "top top",
        end: () => `+=${distance() + window.innerHeight * 0.55}`,
        pin: ".services__pin",
        pinSpacing: true,
        scrub: 0.9,
        anticipatePin: 1,
        invalidateOnRefresh: true,
        onUpdate: (self) => {
          setProgress(0.1 + self.progress * 0.9);
        },
      },
    });

    return () => {
      tween.scrollTrigger?.kill();
      tween.kill();
      gsap.set(track, { clearProps: "transform" });
      setProgress(0.1);
    };
  });
}
