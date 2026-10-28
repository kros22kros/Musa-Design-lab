/**
 * Control de los videos: showreel con play editorial y reel vertical.
 */
export function initVideos() {
  const showreel = document.querySelector("[data-showreel]");
  const video = showreel?.querySelector(".showreel__video");
  const play = showreel?.querySelector("[data-showreel-play]");

  const startShowreel = () => {
    if (!video) return;
    showreel.classList.add("is-playing");
    video.controls = true;
    video.play().catch(() => {});
  };

  play?.addEventListener("click", startShowreel);

  video?.addEventListener("ended", () => {
    showreel.classList.remove("is-playing");
    video.controls = false;
  });

  // Los videos silenciosos suelen reproducirse solos; reforzamos el intento
  // en el primer gesto del usuario por si el navegador los bloquea.
  const ambient = [...document.querySelectorAll(".hero__video, .phone__video")];

  const tryPlay = () => {
    ambient.forEach((v) => v.play().catch(() => {}));
  };

  tryPlay();
  document.addEventListener("pointerdown", tryPlay, { once: true });
}
