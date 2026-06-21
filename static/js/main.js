// Accordion blocks
document.querySelectorAll('.accordion-trigger').forEach(trigger => {
  trigger.addEventListener('click', () => {
    const expanded = trigger.getAttribute('aria-expanded') === 'true';
    const panel = document.getElementById(trigger.getAttribute('aria-controls'));

    // Collapse all siblings in the same accordion
    const accordion = trigger.closest('.block-accordion');
    accordion.querySelectorAll('.accordion-trigger').forEach(t => {
      t.setAttribute('aria-expanded', 'false');
      const p = document.getElementById(t.getAttribute('aria-controls'));
      if (p) p.hidden = true;
    });

    // Toggle this one
    if (!expanded) {
      trigger.setAttribute('aria-expanded', 'true');
      if (panel) panel.hidden = false;
    }
  });
});

// Smooth active highlight on quick-nav scroll
// (also wired inline on homepage template with page-specific sections)
(function () {
  const sections = document.querySelectorAll('section[id]');
  const navItems = document.querySelectorAll('.qnav-item');
  if (!sections.length || !navItems.length) return;

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navItems.forEach(item => {
          item.classList.toggle('active',
            item.getAttribute('href') === '#' + entry.target.id);
        });
      }
    });
  }, { threshold: 0.35 });

  sections.forEach(s => observer.observe(s));
})();
