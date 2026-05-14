/*  */(function () {
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
  document.querySelectorAll('.per-page-btn').forEach(a => {
    a.addEventListener('click', function () {
      const u = new URL(this.href, location.origin);
      localStorage.setItem(KEY, u.searchParams.get('per_page'));
    });
  });
})();

(function () {
  const data = window.INDEX_TAG_DATA;
  if (!data) return;
  const input = document.getElementById('tagSearchInput');
  const dropdown = document.getElementById('tagSearchDropdown');
  if (!input) return;

  function render(query) {
    const q = query.toLowerCase();
    const matches = q ? data.allTags.filter(t => t.toLowerCase().includes(q)) : [];
    dropdown.innerHTML = '';
    matches.forEach(tag => {
      const item = document.createElement('div');
      item.className = 'tag-search-item';
      item.textContent = tag;
      item.addEventListener('mousedown', function (e) {
        e.preventDefault();
        window.location = '?filter=' + data.filter + '&per_page=' + data.perPage + '&tag=' + encodeURIComponent(tag);
      });
      dropdown.appendChild(item);
    });
    dropdown.classList.toggle('is-open', matches.length > 0);
  }

  input.addEventListener('input', () => render(input.value));
  input.addEventListener('focus', () => render(input.value));
  input.addEventListener('blur', () => dropdown.classList.remove('is-open'));
})();

function toggleSave(btn) {
  const debateId = btn.dataset.debateId;
  const isSaved = btn.classList.contains('is-saved');
  const endpoint = isSaved ? 'unsave' : 'save';
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

  fetch(`/api/debates/${debateId}/${endpoint}`, {
    method: 'POST',
    headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'application/json' },
  })
    .then(r => r.json())
    .then(data => {
      btn.classList.toggle('is-saved', data.saved);
      btn.textContent = data.saved ? '// saved' : '// save';
    });
}
