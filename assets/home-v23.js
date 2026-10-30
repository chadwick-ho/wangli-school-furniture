/* Manual scene selection: stable reading, keyboard access, no autoplay. */
(() => {
  const hero = document.querySelector('.wl-v23-hero');
  if (!hero) return;
  const buttons = [...hero.querySelectorAll('[data-scene]')];
  const status = hero.querySelector('[aria-live]');
  function show(index, focus) {
    buttons.forEach((button, i) => {
      const active = i === index;
      button.setAttribute('aria-pressed', String(active));
      document.getElementById(button.getAttribute('aria-controls')).hidden = !active;
      if (active && focus) button.focus();
    });
    if (status) status.textContent = buttons[index].textContent.trim();
  }
  buttons.forEach((button, index) => {
    button.addEventListener('click', () => show(index, false));
    button.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? buttons.length - 1 :
        (index + (event.key === 'ArrowLeft' ? 1 : -1) + buttons.length) % buttons.length;
      show(next, true);
    });
  });
})();
