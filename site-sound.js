// Provide the V Space hero sound and restrained glassy interaction feedback.
(() => {
  const heroSound = new Audio("./assets/sound/hero-astonishment.wav");
  const clickSource = "./assets/sound/glassy-snap.wav";

  const HERO_VOLUME = 0.32;
  const HERO_START_OFFSET = 0.30;
  const HERO_FADE_START = 5710;
  const HERO_FADE_DURATION = 900;

  heroSound.preload = "auto";
  heroSound.volume = HERO_VOLUME;

  let fadeTimer = null;
  let fadeInterval = null;

  function clearHeroTimers() {
    if (fadeTimer) clearTimeout(fadeTimer);
    if (fadeInterval) clearInterval(fadeInterval);
    fadeTimer = null;
    fadeInterval = null;
  }

  function playHero() {
    clearHeroTimers();

    heroSound.pause();
    heroSound.currentTime = HERO_START_OFFSET;
    heroSound.volume = HERO_VOLUME;

    const attempt = heroSound.play();

    if (attempt?.catch) {
      attempt.catch(() => {});
    }

    fadeTimer = setTimeout(() => {
      const started = performance.now();

      fadeInterval = setInterval(() => {
        const progress = Math.min(
          1,
          (performance.now() - started) / HERO_FADE_DURATION
        );

        heroSound.volume = HERO_VOLUME * (1 - progress);

        if (progress >= 1) {
          clearInterval(fadeInterval);
          fadeInterval = null;
          heroSound.pause();
          heroSound.volume = HERO_VOLUME;
        }
      }, 30);
    }, HERO_FADE_START);
  }

  function playClick() {
    const sound = new Audio(clickSource);
    sound.volume = 0.20;
    sound.play().catch(() => {});
  }

  document.addEventListener("click", event => {
    const control = event.target.closest(
      "button, a, select, input[type='file'], [role='button']"
    );

    if (!control || control.disabled) return;

    playClick();
  });

  window.VSpaceSound = {
    playHero
  };
})();
