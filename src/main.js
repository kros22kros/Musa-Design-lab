import "@fontsource/cormorant-garamond/latin-300.css";
import "@fontsource/cormorant-garamond/latin-400.css";
import "@fontsource/cormorant-garamond/latin-500.css";
import "@fontsource/cormorant-garamond/latin-300-italic.css";
import "@fontsource/cormorant-garamond/latin-400-italic.css";
import "@fontsource/jost/latin-300.css";
import "@fontsource/jost/latin-400.css";
import "@fontsource/jost/latin-500.css";

import "./styles/tokens.css";
import "./styles/base.css";
import "./styles/chrome.css";
import "./styles/sections.css";
import "./styles/responsive.css";

import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import { createSmoothScroll, bindAnchors } from "./js/smooth.js";
import { playPreloader } from "./js/preloader.js";
import { createHeroIntro, initHeroParallax } from "./js/hero.js";
import { initReveals, initScrollUI } from "./js/reveals.js";
import { initServices } from "./js/services.js";
import { initProcess } from "./js/process.js";
import { initCursor } from "./js/cursor.js";
import { initMenu } from "./js/menu.js";
import { initTabs } from "./js/tabs.js";
import { initGallery } from "./js/gallery.js";
import { initVideos } from "./js/video.js";
import { initForm } from "./js/form.js";
import { applySiteConfig } from "./js/social.js";

gsap.registerPlugin(ScrollTrigger);
ScrollTrigger.config({ ignoreMobileResize: true });

const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if ("scrollRestoration" in history) {
  history.scrollRestoration = "manual";
}
window.scrollTo(0, 0);

document.body.classList.add("is-locked");

async function boot() {
  applySiteConfig();

  const { lenis, scrollTo } = createSmoothScroll(reduced);
  const menu = initMenu({ lenis });

  const heroIntro = createHeroIntro(reduced);
  initCursor(reduced);
  initTabs();
  initGallery({ lenis });
  initVideos();
  initForm();

  bindAnchors(scrollTo, () => menu?.close());

  // Esperamos las tipografías para partir los titulares con precisión.
  try {
    await document.fonts.ready;
  } catch {
    /* si falla, seguimos con las fuentes del sistema */
  }

  initReveals(reduced);
  initServices(reduced);
  initProcess(reduced);
  initScrollUI();
  initHeroParallax(reduced);

  ScrollTrigger.refresh();

  await playPreloader({
    reduced,
    onReveal: () => {
      document.body.classList.remove("is-locked");
      lenis?.start();
      heroIntro?.play(0);
      document.documentElement.classList.add("is-ready");
    },
  });
}

boot();
