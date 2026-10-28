# MUSA — Sitio web

Sitio de una sola página para **MUSA**, estudio creativo de comunicación y
presencia digital. Construido con Vite, JavaScript vanilla, GSAP y Lenis, con
un universo visual generado a medida (imágenes y videos) para la marca.

> **Dónde las ideas encuentran su voz.**

---

## Stack

- **Vite 8** — build y servidor de desarrollo.
- **GSAP + ScrollTrigger** — animaciones, pin horizontal, reveals y parallax.
- **Lenis** — scroll suave sincronizado con ScrollTrigger.
- **SplitType** — titulares partidos por líneas.
- **@fontsource** — Cormorant Garamond y Jost autoalojadas (sin Google Fonts).
- **CSS moderno** — custom properties, `clamp()`, grid, `svh`, `prefers-reduced-motion`.

Sin frameworks de UI y sin dependencias de imágenes de stock.

---

## Estructura

```
MUSA-Web/
├─ index.html               # Todo el contenido y la semántica del sitio
├─ public/
│  ├─ media/                # Imágenes y videos generados (jpg, webp, mp4)
│  ├─ favicon.svg
│  ├─ grain.png
│  ├─ og-image.jpg
│  ├─ robots.txt
│  └─ sitemap.xml
├─ src/
│  ├─ main.js               # Arranque, orden de módulos y preloader
│  ├─ data/site.js          # ⚠️ Correo y redes sociales editables
│  ├─ js/
│  │  ├─ smooth.js          # Lenis + anclas internas
│  │  ├─ preloader.js       # Cortina de entrada (con failsafe)
│  │  ├─ hero.js            # Intro y parallax del hero
│  │  ├─ reveals.js         # Reveals, split headings, contadores, nav activa
│  │  ├─ services.js        # Carrusel horizontal con pin
│  │  ├─ process.js         # Progreso de pasos
│  │  ├─ tabs.js            # Propósito / Misión / Visión
│  │  ├─ gallery.js         # Filtros + lightbox accesible
│  │  ├─ video.js           # Showreel y videos ambientales
│  │  ├─ menu.js            # Menú móvil
│  │  ├─ form.js            # Validación + mailto
│  │  ├─ social.js          # Inyecta correo, redes y año
│  │  └─ cursor.js          # Cursor personalizado
│  └─ styles/
│     ├─ tokens.css         # Color, tipografía, layout, motion
│     ├─ base.css           # Reset, tipografía, botones, preloader
│     ├─ chrome.css         # Nav, menú, footer, lightbox
│     ├─ sections.css       # Secciones del sitio
│     └─ responsive.css     # Ajustes por breakpoint
└─ tools/generate_assets.py # Generador reproducible de todo el media
```

---

## Comandos

```bash
npm install      # instalar dependencias
npm run dev      # desarrollo en http://localhost:5173
npm run build    # build de producción en dist/
npm run preview  # servir dist/ en http://localhost:4173
```

Requiere **Node 22.12+** (ver `.nvmrc`).

---

## Contenido editable

Todo el copy vive en `index.html`. Los datos de contacto están centralizados:

```js
// src/data/site.js
export const site = {
  email: "hola@musa.studio",              // ← correo real
  social: {
    instagram: "https://www.instagram.com/", // ← perfil real
    tiktok: "https://www.tiktok.com/",
    facebook: "https://www.facebook.com/",
  },
};
```

El formulario no usa backend: valida los campos y abre el gestor de correo con
el mensaje preparado (`mailto:`). Si más adelante se quiere un envío real, se
puede sustituir el bloque de `mailto` en `src/js/form.js` por Formspree, Resend
o una función serverless de Vercel.

### Dominio y metadatos

Cuando exista el dominio definitivo, actualizar:

- `index.html` — `canonical`, `og:url`, JSON-LD (`url`, `logo`).
- `public/robots.txt` — línea `Sitemap`.
- `public/sitemap.xml` — `<loc>`.

---

## Universo visual

Todas las imágenes y videos son originales y se generan por código, sin bancos
de imágenes ni licencias externas:

- 6 piezas editoriales del portafolio (1200×1500) en `.jpg` y `.webp`.
- 3 placas abstractas del equipo (1000×1250) en `.jpg` y `.webp`.
- `hero.mp4` (10 s), `reel.mp4` (8 s vertical) y `showreel.mp4` (16 s) con sus
  posters.
- `og-image.jpg` (1200×630), `footer-musa.png` (marca de agua del pie),
  `grain.png` y `favicon.svg`.

Para regenerarlos:

```bash
pip install pillow numpy imageio-ffmpeg
python tools/generate_assets.py
```

El script usa las fuentes de `tools/fonts/` y `ffmpeg` incluido en
`imageio-ffmpeg`. Tarda unos minutos porque renderiza los videos cuadro a cuadro.

---

## Despliegue en Vercel

### Opción A — desde GitHub (recomendada)

1. Subir el repositorio a GitHub.
2. En Vercel: **Add New → Project → Import Git Repository**.
3. Framework preset: **Vite**. Build: `npm run build`. Output: `dist`.
4. Deploy. `vercel.json` ya define build, `dist`, `cleanUrls` y cache de
   `/media` y `/assets`.

### Opción B — CLI

```bash
npm i -g vercel
vercel          # preview
vercel --prod   # producción
```

---

## Notas de accesibilidad y rendimiento

- HTML semántico, un solo `h1`, landmarks y enlace «Saltar al contenido».
- Tabs con roles ARIA y navegación por flechas / Home / End.
- Lightbox con `dialog`, foco gestionado, `inert` en el resto del documento,
  cierre con `Escape` y navegación con flechas.
- Formulario con `label` asociados, validación nativa y mensajes de estado.
- Respeta `prefers-reduced-motion`: sin preloader, sin animaciones y contenido
  siempre visible.
- Imágenes con `width`/`height` o `aspect-ratio`, `loading="lazy"` y `<picture>`
  con WebP. Fuentes autoalojadas y subset latin.
- El preloader tiene un failsafe de 7 s para pestañas en segundo plano.

---

## Portafolio

Las piezas de la sección «Universo visual» son **trabajos conceptuales** creados
para explorar la identidad de MUSA, no proyectos de clientes. El sitio lo indica
explícitamente para evitar atribuciones falsas.

---

© 2026 MUSA — Isabella Corredor, Emilia Macias, Elizabeth Román.
