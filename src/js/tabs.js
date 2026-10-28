/**
 * Pestañas accesibles: Propósito / Misión / Visión.
 */
export function initTabs() {
  const root = document.querySelector("[data-tabs]");
  if (!root) return;

  const buttons = [...root.querySelectorAll("[data-tab]")];
  const panels = [...root.querySelectorAll("[data-panel]")];

  const activate = (key, focus = false) => {
    buttons.forEach((button) => {
      const isActive = button.dataset.tab === key;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-selected", String(isActive));
      button.tabIndex = isActive ? 0 : -1;
      if (isActive && focus) button.focus();
    });

    panels.forEach((panel) => {
      const isActive = panel.dataset.panel === key;
      panel.classList.toggle("is-active", isActive);
      if (isActive) panel.removeAttribute("hidden");
      else panel.setAttribute("hidden", "");
    });
  };

  buttons.forEach((button, index) => {
    button.addEventListener("click", () => activate(button.dataset.tab));

    button.addEventListener("keydown", (event) => {
      let next = null;

      if (event.key === "ArrowRight") next = (index + 1) % buttons.length;
      if (event.key === "ArrowLeft")
        next = (index - 1 + buttons.length) % buttons.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = buttons.length - 1;

      if (next !== null) {
        event.preventDefault();
        activate(buttons[next].dataset.tab, true);
      }
    });
  });
}
