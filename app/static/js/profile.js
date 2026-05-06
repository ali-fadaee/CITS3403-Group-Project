/* ══════════════════════════════
       AVATAR
    ══════════════════════════════ */
    const FACES = [
      '🤖','👾','🦾','🧠','👽','🐲','🦊',
      '🐺','🦁','🐯','🦅','🐙','🦑','🦂',
      '🧟','🧛','🧙','🥷','👻','💀','🃏',
      '🦇','🐉','🔮','🛸','⚡','🌑','🎭'
    ];
    let selectedFace = '🤖';

    const avatarDisplay = document.getElementById('avatarDisplay');
    const avatarGrid    = document.getElementById('avatarGrid');

    FACES.forEach(f => {
      const btn = document.createElement('button');
      btn.className = 'avatar-option' + (f === selectedFace ? ' is-selected' : '');
      btn.textContent = f;
      btn.addEventListener('click', () => {
        avatarGrid.querySelectorAll('.avatar-option').forEach(b => b.classList.remove('is-selected'));
        btn.classList.add('is-selected');
        avatarDisplay.textContent = f;
        selectedFace = f;
        setTimeout(closeAvatarModal, 180);
      });
      avatarGrid.appendChild(btn);
    });

    function openAvatarModal() {
      document.getElementById('avatarBackdrop').classList.add('is-open');
      document.getElementById('avatarModal').classList.add('is-open');
    }
    function closeAvatarModal() {
      document.getElementById('avatarBackdrop').classList.remove('is-open');
      document.getElementById('avatarModal').classList.remove('is-open');
    }

    /* ══════════════════════════════
       INTERESTS
    ══════════════════════════════ */
    const ALL_CATEGORIES = [
      'politics','AI ethics','climate','philosophy','economics',
      'technology','science','history','law','psychology',
      'geopolitics','religion','education','healthcare','media',
      'culture','finance','military','environment','human rights',
      'energy','space','sport','urbanism','nutrition'
    ];

    const activeInterests = new Set(['politics','AI ethics','climate','philosophy','economics','technology']);

    const interestsRow = document.getElementById('interestsRow');
    const addBtn       = document.getElementById('addInterestBtn');
    const categoryGrid = document.getElementById('categoryGrid');

    // build chips
    ALL_CATEGORIES.forEach(cat => {
      const chip = document.createElement('button');
      chip.className = 'category-chip' + (activeInterests.has(cat) ? ' is-selected' : '');
      chip.textContent = cat;
      chip.dataset.cat = cat;
      chip.addEventListener('click', () => {
        if (activeInterests.has(cat)) {
          activeInterests.delete(cat);
          chip.classList.remove('is-selected');
        } else {
          activeInterests.add(cat);
          chip.classList.add('is-selected');
        }
        renderTags();
      });
      categoryGrid.appendChild(chip);
    });

    function renderTags() {
      [...interestsRow.children].forEach(el => { if (el !== addBtn) el.remove(); });
      ALL_CATEGORIES.filter(c => activeInterests.has(c)).forEach(cat => {
        const tag = document.createElement('span');
        tag.className = 'interest-tag';
        const label = document.createTextNode(cat + '\u00a0');
        const rm = document.createElement('button');
        rm.className = 'interest-remove';
        rm.textContent = '✕';
        rm.addEventListener('click', () => {
          activeInterests.delete(cat);
          const chip = categoryGrid.querySelector(`[data-cat="${cat}"]`);
          if (chip) chip.classList.remove('is-selected');
          renderTags();
        });
        tag.appendChild(label);
        tag.appendChild(rm);
        interestsRow.insertBefore(tag, addBtn);
      });
    }

    function openInterestsModal() {
      document.getElementById('interestsBackdrop').classList.add('is-open');
      document.getElementById('interestsModal').classList.add('is-open');
    }
    function closeInterestsModal() {
      document.getElementById('interestsBackdrop').classList.remove('is-open');
      document.getElementById('interestsModal').classList.remove('is-open');
    }

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') { closeAvatarModal(); closeInterestsModal(); }
    });

    /* ══════════════════════════════
       PASSWORD
    ══════════════════════════════ */
    function togglePassword() {
      const f = document.getElementById('passwordField');
      if (f.readOnly) {
        f.readOnly = false; f.type = 'text'; f.value = ''; f.focus();
      } else {
        f.readOnly = true; f.type = 'password'; f.value = '';
      }
    }

    renderTags();

    /* ══════════════════════════════
       SAVE PROFILE
       ══════════════════════════════ */
    document.getElementById('saveProfileBtn').addEventListener('click', async function () {
      const btn      = this;
      const password = document.getElementById('passwordField');
      const body     = {};

      if (!password.readOnly && password.value.trim()) {
        body.password = password.value.trim();
      }

      if (!Object.keys(body).length) {
        alert('// nothing to save');
        return;
      }

      btn.disabled = true;
      btn.textContent = '$ saving...';

      try {
        const res = await fetch('/api/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        const data = await res.json();
        if (res.ok) {
          btn.textContent = '$ saved ✓';
          password.readOnly = true;
          password.type = 'password';
          password.value = '';
          setTimeout(() => { btn.textContent = '$ save --apply'; btn.disabled = false; }, 2000);
        } else {
          alert('// error: ' + (data.error || 'save failed'));
          btn.disabled = false;
          btn.textContent = '$ save --apply';
        }
      } catch (err) {
        alert('// error: network failure');
        btn.disabled = false;
        btn.textContent = '$ save --apply';
      }
    });

    /*�