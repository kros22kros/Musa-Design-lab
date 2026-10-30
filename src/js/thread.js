/**
 * Hilo de luz: un trazo único que desciende por el margen derecho y
 * acompaña el avance de la lectura. No tiene movimiento propio: solo
 * responde al scroll, con una chispa en la punta del recorrido.
 */
export function initThread() {
  const root = document.querySelector(".thread");
  const path = root?.querySelector(".thread__trace");
  const spark = root?.querySelector(".thread__spark");
  if (!root || !path || !spark) return;

  const length = path.getTotalLength();
  let width = 0;
  let height = 0;
  let frame = 0;

  const measure = () => {
    const box = root.getBoundingClientRect();
    width = box.width;
    height = box.height;
  };

  const draw = () => {
    frame = 0;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const progress = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;

    path.style.strokeDashoffset = String(1000 * (1 - progress));

    const point = path.getPointAtLength(length * progress);
    const x = (point.x / 120) * width - 3;
    const y = (point.y / 1000) * height - 3;
    spark.style.transform = `translate3d(${x}px, ${y}px, 0) rotate(45deg)`;
  };

  const queue = () => {
    if (!frame) frame = requestAnimationFrame(draw);
  };

  measure();
  draw();
  window.addEventListener("scroll", queue, { passive: true });
  window.addEventListener("resize", () => {
    measure();
    draw();
  });
  window.addEventListener("load", queue);
}
