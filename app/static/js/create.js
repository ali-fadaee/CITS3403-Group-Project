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

  createBtn.addEventListener('click', async function () {
    const thesis   = document.getElementById('thesisInput').value.trim();
    const selectedCategories = [...document.querySelectorAll('#createCategoryGrid .category-chip.is-selected')]
      .map(btn => btn.dataset.cat);
    
    if (!thesis) {
      alert('// error: --thesis cannot be empty');
      return;
    }

    if (!selectedCategories.length) {
      alert('// error: select at least one category');
      return;
    }
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
        closeModal('createModal');
        window.location.replace('/debate/' + data.id);
      } else {
        alert('// error: ' + (data.error || 'failed to create debate'));
        createBtn.disabled = false;
        createBtn.textContent = '$ create --execute';
      }
    } catch (err) {
      alert('// error: network failure');
      createBtn.disabled = false;
      createBtn.textContent = '$ create --execute';
    }
  });
});