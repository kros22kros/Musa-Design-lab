import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export function initGallery({ lenis = null } = {}) {
  const gallery = document.querySelector("[data-gallery]");
  const filters = document.querySelector("[data-filters]");
  const modal = document.querySelector("[data-lightbox-modal]");

  if (!gallery) return;

  const items = [...gallery.querySelectorAll("[data-lightbox]")];
  const filterButtons = filters
    ? [...filters.querySelectorAll("[data-filter]")]
    : [];

  let lastFocused = null;

  const visibleItems = () => items.filter((item) => !item.classList.contains("is-hidden"));

  /* ---------------- Filtros ---------------- */
  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const filter = button.dataset.filter;

      filterButtons.forEach((b) => b.classList.toggle("is-active", b === button));

      items.forEach((item) => {
        const match = filter === "all" || item.dataset.cat === filter;
        item.classList.toggle("is-hidden", !match);
      });

      ScrollTrigger.refresh();
    });
  });

  if (!modal) return;

  const image = modal.querySelector("[data-lightbox-img]");
  const caption = modal.querySelector("[data-lightbox-caption]");
  const closeBtn = modal.querySelector("[data-lightbox-close]");
  const prevBtn = modal.querySelector("[data-lightbox-prev]");
  const nextBtn = modal.querySelector("[data-lightbox-next]");
  const main = document.querySelector("main");
  const footer = document.querySelector(".footer");

  let index = 0;
  let open = false;

  const render = () => {
    const list = visibleItems();
    const item = list[index];
    if (!item) return;

    const thumb = item.querySelector("img");
    image.src = item.dataset.src;
    image.alt = thumb?.alt || "";
    caption.textContent = item.dataset.caption || "";

    gsap.fromTo(
      image,
      { opacity: 0, scale: 0.97 },
      { opacity: 1, scale: 1, duration: 0.55, ease: "power3.out" }
    );
  };

  const openAt = (item) => {
    const list = visibleItems();
    index = Math.max(0, list.indexOf(item));
    lastFocused = document.activeElement;

    render();
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("is-locked");
    if (main) main.inert = true;
    if (footer) footer.inert = true;
    lenis?.stop();

    open = true;
    window.setTimeout(() => closeBtn.focus(), 60);
  };

  const close = () => {
    if (!open) return;
    open = false;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("is-locked");
    if (main) main.inert = false;
    if (footer) footer.inert = false;
    lenis?.start();
    lastFocused?.focus?.({ preventScroll: true });
  };

  const step = (direction) => {
    const list = visibleItems();
    if (!list.length) return;
    index = (index + direction + list.length) % list.length;
    render();
  };

  items.forEach((item) => {
    item.addEventListener("click", () => openAt(item));
    item.setAttribute("data-cursor", "Ver");
  });

  closeBtn?.addEventListener("click", close);
  prevBtn?.addEventListener("click", () => step(-1));
  nextBtn?.addEventListener("click", () => step(1));

  modal.addEventListener("click", (event) => {
    if (event.target === modal) close();
  });

  document.addEventListener("keydown", (event) => {
    if (!open) return;
    if (event.key === "Escape") close();
    if (event.key === "ArrowLeft") step(-1);
    if (event.key === "ArrowRight") step(1);
  });
}
