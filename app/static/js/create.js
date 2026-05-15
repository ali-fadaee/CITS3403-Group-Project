document.addEventListener('DOMContentLoaded', function () {
  const createGrid = document.getElementById('createCategoryGrid');
  if (createGrid) {
    fetch('/api/tags')
      .then(res => res.ok ? res.json() : [])
      .then(categories => {
        categories.forEach(cat => {
          const chip = document.createElement('button');
          chip.type = 'button';
          chip.className = 'category-chip';
          chip.textContent = cat;
          chip.dataset.cat = cat;
          chip.addEventListener('click', () => chip.classList.toggle('is-selected'));
          createGrid.appendChild(chip);
        });
      });
  }
  const createBtn = document.getElementById('createDebateBtn');
  if (!createBtn) return;

  function showCreateError(msg) {
    const el = document.getElementById('createError');
    el.textContent = msg;
    el.style.display = 'inline';
  }
  function clearCreateError() {
    const el = document.getElementById('createError');
    el.textContent = '';
    el.style.display = 'none';
  }

  createBtn.addEventListener('click', async function () {
    const thesis   = document.getElementById('thesisInput').value.trim();
    const selectedCategories = [...document.querySelectorAll('#createCategoryGrid .category-chip.is-selected')]
      .map(btn => btn.dataset.cat);

    if (!thesis) {
      showCreateError('// debate cannot be empty');
      return;
    }

    if (!selectedCategories.length) {
      showCreateError('// select at least one category');
      return;
    }
    clearCreateError();
    createBtn.disabled = true;
    createBtn.textContent = '$ creating...';

    try {
      const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
      const res = await fetch('/api/debates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify({ title: thesis, categories: selectedCategories })
      });
      const data = await res.json();
      if (res.ok) {
        clearCreateError();
        closeModal('createModal');
        window.location.replace('/debate/' + data.id);
      } else {
        showCreateError('// ' + (data.error || 'failed to create debate'));
        createBtn.disabled = false;
        createBtn.textContent = '$ create --execute';
      }
    } catch (err) {
      showCreateError('// network failure');
      createBtn.disabled = false;
      createBtn.textContent = '$ create --execute';
    }
  });
});
