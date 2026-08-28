(() => {
  const root = document.documentElement;
  const savedTheme = localStorage.getItem('pf-theme');
  if (savedTheme) root.dataset.theme = savedTheme;

  document.querySelector('.theme-toggle')?.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    localStorage.setItem('pf-theme', next);
  });

  const progress = document.querySelector('.reading-progress span');
  const updateProgress = () => {
    if (!progress) return;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const pct = max > 0 ? Math.min(100, Math.max(0, window.scrollY / max * 100)) : 0;
    progress.style.width = `${pct}%`;
  };
  updateProgress();
  window.addEventListener('scroll', updateProgress, { passive: true });
  window.addEventListener('resize', updateProgress);

  document.querySelectorAll('.video-card').forEach((card) => {
    const button = card.querySelector('.video-poster');
    button?.addEventListener('click', () => {
      const id = card.dataset.videoId;
      if (!id) return;
      const iframe = document.createElement('iframe');
      iframe.src = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}?autoplay=1&rel=0`;
      iframe.title = button.getAttribute('aria-label') || 'Embedded video';
      iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      iframe.allowFullscreen = true;
      card.replaceChildren(iframe);
    });
  });

  const tocLinks = [...document.querySelectorAll('.toc a')];
  const sections = tocLinks.map((a) => document.querySelector(a.getAttribute('href'))).filter(Boolean);
  if ('IntersectionObserver' in window && sections.length) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      tocLinks.forEach((link) => link.classList.toggle('current', link.getAttribute('href') === `#${visible.target.id}`));
    }, { rootMargin: '-18% 0px -68% 0px', threshold: [0, .2, .5] });
    sections.forEach((section) => observer.observe(section));
  }
})();
