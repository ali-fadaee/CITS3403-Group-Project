(function () {
  const KEY = 'debatePerPage';
  const params = new URLSearchParams(location.search);
  if (params.has('per_page')) {
    localStorage.setItem(KEY, params.get('per_page'));
  } else {
    const saved = localStorage.getItem(KEY);
    if (saved && ['10', '25', '50', '100'].includes(saved)) {
      params.set('per_page', saved);
      location.replace('?' + params.toString());
    }
  }
  document.querySelectorAll('.per-page-tabs a').forEach(a => {
    a.addEventListener('click', function () {
      const u = new URL(this.href, location.origin);
      localStorage.setItem(KEY, u.searchParams.get('per_page'));
    });
  });
})();
