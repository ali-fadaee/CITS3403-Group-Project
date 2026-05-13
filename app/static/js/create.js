document.addEventListener('DOMContentLoaded', function () {
  const createBtn = document.getElementById('createDebateBtn');
  if (!createBtn) return;

  createBtn.addEventListener('click', async function () {
    const thesis   = document.getElementById('thesisInput').value.trim();
    const category = document.getElementById('categorySelect').value;

    if (!thesis) {
      alert('// error: --thesis cannot be empty');
      return;
    }

    createBtn.disabled = true;
    createBtn.textContent = '$ creating...';

    try {
      const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
      const res = await fetch('/api/debates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify({ title: thesis, category: category })
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