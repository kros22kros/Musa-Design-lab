import gsap from "gsap";

/**
 * Preloader editorial: conteo, barra dorada y cortina.
 * Devuelve una promesa que se resuelve al terminar la salida.
 *
 * Incluye un failsafe: si la pestaña está en segundo plano (rAF en pausa)
 * o algo falla, la cortina se retira de todos modos para no bloquear el sitio.
 */
export function playPreloader({ reduced = false, onReveal } = {}) {
  const el = document.querySelector("#preloader");
  if (!el) {
    onReveal?.();
    return Promise.resolve();
  }

  if (reduced) {
    el.style.display = "none";
    onReveal?.();
    return Promise.resolve();
  }

  const count = el.querySelector(".preloader__count");
  const bar = el.querySelector(".preloader__bar span");
  const state = { value: 0 };

  const update = () => {
    const n = Math.round(state.value);
    if (count) count.textContent = String(n).padStart(2, "0");
    if (bar) bar.style.transform = `scaleX(${n / 100})`;
  };

  const loaded = new Promise((resolve) => {
    if (document.readyState === "complete") resolve();
    else window.addEventListener("load", resolve, { once: true });
  });

  const minimum = new Promise((resolve) => setTimeout(resolve, 1100));
  const maximum = new Promise((resolve) => setTimeout(resolve, 4200));

  const counter = gsap.to(state, {
    value: 100,
    duration: 1.5,
    ease: "power2.inOut",
    onUpdate: update,
  });

  return new Promise((resolve) => {
    let finished = false;
    let revealed = false;

    const reveal = () => {
      if (revealed) return;
      revealed = true;
      onReveal?.();
    };

    const finish = () => {
      if (finished) return;
      finished = true;
      window.clearTimeout(failsafe);
      counter.kill();
      update();
      el.style.display = "none";
      reveal();
      resolve();
    };

    const failsafe = window.setTimeout(finish, 7000);

    Promise.race([
      Promise.all([loaded, minimum, new Promise((r) => setTimeout(r, 1500))]),
      maximum,
    ]).then(() => {
      if (finished) return;

      counter.kill();
      update();

      const tl = gsap.timeline({ onComplete: finish });

      tl.to(".preloader__inner", {
        opacity: 0,
        y: -18,
        duration: 0.45,
        ease: "power2.in",
      }).to(
        el,
        {
          yPercent: -100,
          duration: 1.05,
          ease: "expo.inOut",
          onStart: reveal,
        },
        0.12
      );
    });
  });
}
