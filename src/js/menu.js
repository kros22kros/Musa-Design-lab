/**
 * Menú móvil a pantalla completa con bloqueo de scroll.
 */
export function initMenu({ lenis = null } = {}) {
  const nav = document.querySelector("#nav");
  const toggle = document.querySelector(".nav__toggle");
  const menu = document.querySelector("#menu");
  const links = [...document.querySelectorAll(".menu__links a")];

  if (!toggle || !menu) return null;

  let open = false;

  const setOpen = (value) => {
    open = value;
    toggle.setAttribute("aria-expanded", String(value));
    toggle.setAttribute("aria-label", value ? "Cerrar menú" : "Abrir menú");
    menu.classList.toggle("is-open", value);
    menu.setAttribute("aria-hidden", String(!value));
    nav?.classList.toggle("is-menu", value);
    document.body.classList.toggle("is-locked", value);

    if (value) {
      lenis?.stop();
      window.setTimeout(() => links[0]?.focus({ preventScroll: true }), 450);
    } else {
      document.body.classList.remove("is-locked");
      lenis?.start();
    }
  };

  toggle.addEventListener("click", () => setOpen(!open));

  links.forEach((link) => link.addEventListener("click", () => setOpen(false)));

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && open) {
      setOpen(false);
      toggle.focus();
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 1024 && open) setOpen(false);
  });

  return {
    close: () => {
      if (open) setOpen(false);
    },
    isOpen: () => open,
  };
}
