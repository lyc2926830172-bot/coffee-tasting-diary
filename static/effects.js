(() => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.querySelectorAll('.form-grid input, .form-grid select, .form-grid textarea').forEach((field) => {
    const label = field.closest('label');
    if (!label) return;

    field.addEventListener('focus', () => {
      label.classList.add('is-active');
      if (reducedMotion || label.querySelector('.field-particles')) return;

      const particles = document.createElement('span');
      particles.className = 'field-particles';
      for (let index = 0; index < 7; index += 1) {
        const particle = document.createElement('i');
        particle.style.setProperty('--x', `${10 + Math.random() * 80}%`);
        particle.style.setProperty('--delay', `${Math.random() * 280}ms`);
        particle.style.setProperty('--size', `${3 + Math.random() * 4}px`);
        particles.appendChild(particle);
      }
      label.appendChild(particles);
      window.setTimeout(() => particles.remove(), 1250);
    });

    field.addEventListener('blur', () => label.classList.remove('is-active'));
    field.addEventListener('invalid', () => {
      if (reducedMotion) return;
      field.classList.remove('field-nudge');
      requestAnimationFrame(() => field.classList.add('field-nudge'));
    });
    field.addEventListener('animationend', () => field.classList.remove('field-nudge'));
  });
})();
