# MUSA Design Lab — Sitio web

Sitio de una sola página para **MUSA Design Lab**, estudio creativo de
comunicación y presencia digital en Sogamoso, Boyacá. Construido con Vite,
JavaScript vanilla, GSAP y Lenis, con un universo visual generado a medida
(imágenes y videos) para la marca.

> **Dónde las ideas encuentran su voz.**

---

## Stack

- **Vite 8** — build y servidor de desarrollo.
- **GSAP + ScrollTrigger** — animaciones, pin horizontal, reveals y parallax.
- **Lenis** — scroll suave sincronizado con ScrollTrigger.
- **SplitType** — titulares partidos por líneas.
- **Tipografía Georgia** del sistema, sin webfonts ni peticiones externas.
- **CSS moderno** — custom properties, `clamp()`, grid, `svh`, `prefers-reduced-motion`.

Sin frameworks de UI y sin dependencias de imágenes de stock.

---

## Estructura

```
MUSA-Web/
├─ index.html               # Todo el contenido y la semántica del sitio
├─ public/
│  ├─ media/                # Imágenes y videos generados (jpg, webp, mp4)
│  │  └─ brand/             # Logotipo, lockups, favicon y marca de agua
│  ├─ grain.png
│  ├─ og-image.jpg
│  ├─ robots.txt
│  └─ sitemap.xml
├─ src/
│  ├─ main.js               # Arranque, orden de módulos y preloader
│  ├─ data/site.js          # ⚠️ WhatsApp, Instagram y ciudad editables
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
│  │  ├─ thread.js          # Hilo de luz que acompaña el scroll
│  │  ├─ menu.js            # Menú móvil
│  │  ├─ form.js            # Validación + mensaje de WhatsApp
│  │  ├─ social.js          # Inyecta WhatsApp, Instagram, ciudad y año
│  │  └─ cursor.js          # Cursor personalizado
│  └─ styles/
│     ├─ tokens.css         # Paleta de marca, tipografía, layout, motion
│     ├─ base.css           # Reset, tipografía, botones, preloader
│     ├─ chrome.css         # Nav, menú, footer, lightbox
│     ├─ sections.css       # Secciones del sitio
│     └─ responsive.css     # Ajustes por breakpoint
└─ tools/
   ├─ prepare_brand.py      # Extrae el logotipo original y arma los lockups
   ├─ prepare_team.py       # Recorta los retratos reales del equipo a 4:5
   ├─ prepare_video.py      # Deriva el showreel y el reel desde el video de marca
   ├─ generate_assets.py    # Piezas editoriales, texturas e imagen Open Graph
   └─ source/               # JPEG originales de marca, paleta y paquetes
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

## Marca

La identidad parte de los archivos entregados por el estudio:

- **Logotipo:** `tools/source/musa-logotipo.jpeg`, con tipografía negra sobre
  azul plano. `tools/prepare_brand.py` separa el trazo por luminancia del canal
  rojo, lo recolorea y arma los lockups:
  - `logo-stacked-{dark,light}.png` — MUSA sobre *Design Lab* (nav y pie).
  - `logo-horizontal-{dark,light}.png` — lockup horizontal (marca de agua).
  - `logo-script-{dark,light}.png` — solo *Design Lab* (sección El nombre).
  - `favicon.png` — monograma M en vino sobre marfil.
- **Paleta:** `tools/source/paleta-musa.jpeg`. Tokens en `src/styles/tokens.css`:

  | Token | Hex | Uso |
  | --- | --- | --- |
  | `--wine` | `#80231e` | Acento principal, paquetes |
  | `--wine-deep` | `#2b0d10` | Fondos oscuros |
  | `--blue` | `#67768d` | Acento secundario |
  | `--blue-deep` | `#17253a` | Paquete Impulso |
  | `--blue-light` | `#d3d9e7` | Texto y detalles sobre oscuro |
  | `--sky` | `#8aa9c5` | Azul del logotipo original |
  | `--bone` | `#ece9dc` | Fondo claro principal |
  | `--bone-2` / `--cream` | `#e2dfd0` / `#f7f5ec` | Variaciones de fondo |
  | `--ink` | `#0c0b0b` | Texto y fondos negros |

Para regenerar los lockups:

```bash
pip install pillow numpy
python tools/prepare_brand.py
```

---

## Contenido editable

Todo el copy vive en `index.html`. Los datos de contacto están centralizados:

```js
// src/data/site.js
export const site = {
  name: "MUSA Design Lab",
  city: "Sogamoso, Boyacá",
  instagram: {
    handle: "musa_designlab",
    url: "https://www.instagram.com/musa_designlab",
  },
  whatsapp: [
    { number: "573213827782", display: "+57 321 382 7782" }, // principal
    { number: "573214179741", display: "+57 321 417 9741" },
    { number: "573227497053", display: "+57 322 749 7053" },
  ],
};
```

Los enlaces del sitio se hidratan con atributos:

- `[data-wa="0|1|2"]` — abre WhatsApp con el número correspondiente.
  `data-wa-message` precarga el mensaje (por ejemplo, el paquete elegido).
- `[data-social="instagram"]` — perfil de Instagram.
- `[data-insta-handle]`, `[data-city]`, `[data-year]` — textos dinámicos.

El formulario no usa backend: valida los campos y abre WhatsApp con el mensaje
preparado. Si más adelante se quiere un envío real, se puede sustituir el bloque
de `window.open` en `src/js/form.js` por Formspree, Resend o una función
serverless de Vercel.

### Paquetes

La sección «Paquetes» (07) presenta tres propuestas — **Esencial** ($300.000),
**Impulso** ($450.000, destacado) e **Identidad** ($900.000), en COP. Cada CTA
abre WhatsApp con el nombre del paquete en el mensaje. El detalle vive en
`index.html`; los estilos, en `.packages` dentro de `src/styles/sections.css`.

### Dominio y metadatos

Cuando exista el dominio definitivo, actualizar:

- `index.html` — `canonical`, `og:url`, JSON-LD (`url`, `logo`).
- `public/robots.txt` — línea `Sitemap`.
- `public/sitemap.xml` — `<loc>`.

---

## Universo visual

Las piezas editoriales y texturas son originales y se generan por código, sin
bancos de imágenes ni licencias externas. Los retratos del equipo son fotografías
reales de las integrantes, y el showreel y el reel vertical se derivan del video
de marca del estudio:

- 6 piezas editoriales del portafolio (1200×1500) en `.jpg` y `.webp`.
- 3 retratos del equipo (1000×1250) en `.jpg` y `.webp`, recortados a 4:5 desde
  las fotos originales.
- `musa-showreel.mp4` (8 s, 16:9, con audio) y `musa-reel.mp4` (8 s, 9:16,
  silencioso) con sus posters, derivados de `VIDEO DE MUSA.mp4`.
- `og-image.jpg` (1200×630) con el logotipo, `grain.png` y el favicon de marca.

Para regenerar las piezas editoriales y texturas:

```bash
pip install pillow numpy imageio-ffmpeg
python tools/generate_assets.py
```

Los retratos se recortan al formato de las tarjetas del equipo:

```bash
python tools/prepare_team.py
```

Los videos del sitio se derivan del video de marca original:

```bash
python tools/prepare_video.py
```

Los scripts de imágenes usan las fuentes de `tools/fonts/` y el `ffmpeg`
incluido en `imageio-ffmpeg`. Conviene ejecutar `tools/prepare_brand.py` antes,
porque la imagen Open Graph usa los lockups de `public/media/brand/`.

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
  con WebP. Tipografía Georgia del sistema, sin descargas de fuentes.
- El preloader tiene un failsafe de 7 s para pestañas en segundo plano.

---

## Portafolio

Las piezas de la sección «Universo visual» son **trabajos conceptuales** creados
para explorar la identidad de MUSA Design Lab, no proyectos de clientes. El sitio
lo indica explícitamente para evitar atribuciones falsas.

---

© 2026 MUSA Design Lab — Isabella Corredor, Emilia Macias, Elizabeth Román.
