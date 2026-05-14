    /* ══════════════════════════════
        AVATAR
      ══════════════════════════════ */
    let selectedAvatarId = null;
    let avatarGridLoaded = false;

    const avatarDisplay = document.getElementById('avatarDisplay');
    const avatarGrid    = document.getElementById('avatarGrid');

    // Show current avatar immediately from the injected URL — no fetch needed
    if (USER_AVATAR_URL) {
      avatarDisplay.innerHTML = '';
      const current = document.createElement('img');
      current.src = USER_AVATAR_URL;
      avatarDisplay.appendChild(current);
    }

    function loadAvatarGrid() {
      if (avatarGridLoaded) return;
      avatarGridLoaded = true;
      fetch('/api/avatars')
        .then(res => res.json())
        .then(avatars => {
          avatars.forEach(a => {
            const btn = document.createElement('button');
            btn.className = 'avatar-option';
            btn.dataset.avatarId = a.id;

            const img = document.createElement('img');
            img.src = a.url;
            img.alt = a.name;
            btn.appendChild(img);

            if (USER_AVATAR_URL && a.url === USER_AVATAR_URL) {
              btn.classList.add('is-selected');
              selectedAvatarId = a.id;
            }
            btn.addEventListener('click', () => {
              avatarGrid.querySelectorAll('.avatar-option').forEach(b => b.classList.remove('is-selected'));
              btn.classList.add('is-selected');
              avatarDisplay.innerHTML = '';
              const preview = document.createElement('img');
              preview.src = a.url;
              preview.alt = a.name;
              avatarDisplay.appendChild(preview);
              selectedAvatarId = a.id;
              setTimeout(closeAvatarModal, 180);
            });

            avatarGrid.appendChild(btn);
          });
        });
    }

    function openAvatarModal() {
      loadAvatarGrid();
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
    const activeInterests = new Set(typeof USER_INTERESTS !== 'undefined' ? USER_INTERESTS : []);
    const interestsRow = document.getElementById('interestsRow');
    const addBtn       = document.getElementById('addInterestBtn');
    const categoryGrid = document.getElementById('categoryGrid');

    let allCategories = [];

    function buildCategoryChip(cat) {
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
    }

    fetch('/api/tags')
      .then(res => res.json())
      .then(tags => {
        allCategories = tags;
        tags.forEach(buildCategoryChip);
        renderTags();
      })
      .catch(() => {});

    function renderTags() {
      [...interestsRow.children].forEach(el => { if (el !== addBtn) el.remove(); });
      allCategories.filter(c => activeInterests.has(c)).forEach(cat => {
        const tag = document.createElement('span');
        tag.className = 'interest-tag';
        const label = document.createTextNode(cat + ' ');
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
      const fields = document.getElementById('pwChangeFields');
      const btn    = document.getElementById('changePwBtn');

      if (!fields.hidden) {
        fields.hidden = true;
        btn.textContent = '$ change --password';
        document.getElementById('currentPassword').value = '';
        document.getElementById('newPassword').value = '';
        document.getElementById('confirmPassword').value = '';
      } else {
        fields.hidden = false;
        btn.textContent = '$ cancel';
        document.getElementById('currentPassword').focus();
      }
    }


    /* ══════════════════════════════
       BIO COUNTER
    ══════════════════════════════ */
    const bioField = document.getElementById('bioField');
    const bioCount = document.getElementById('bioCount');
    bioField.addEventListener('input', () => { bioCount.textContent = bioField.value.length; });

    function showProfileError(msg) {
      const el = document.getElementById('profileError');
      el.textContent = msg;
      el.style.display = 'inline';
    }
    function clearProfileError() {
      const el = document.getElementById('profileError');
      el.textContent = '';
      el.style.display = 'none';
    }

    /* ══════════════════════════════
       SAVE PROFILE
       ══════════════════════════════ */
    document.getElementById('saveProfileBtn').addEventListener('click', async function () {
      const btn      = this;
      const body     = {};

      const currentPw = document.getElementById('currentPassword').value.trim();
      const newPw     = document.getElementById('newPassword').value.trim();
      const confirmPw = document.getElementById('confirmPassword').value.trim();

      if (currentPw || newPw || confirmPw) {
        if (!currentPw) { showProfileError('// enter your current password'); return; }
        if (!newPw)     { showProfileError('// enter a new password'); return; }
        if (newPw !== confirmPw) { showProfileError('// passwords do not match'); return; }
        if (newPw.length < 8)                { showProfileError('// password too short (min 8 chars)'); return; }
        if (!/[a-z]/.test(newPw))            { showProfileError('// password must contain a lowercase letter'); return; }
        if (!/[A-Z]/.test(newPw))            { showProfileError('// password must contain an uppercase letter'); return; }
        if (!/\d/.test(newPw))               { showProfileError('// password must contain a number'); return; }
        body.current_password = currentPw;
        body.password = newPw;
      }
      if (selectedAvatarId !== null) {
        body.avatar_id = selectedAvatarId;
      }

      const bio = bioField.value.trim();
      if (bio !== (USER_BIO || '').trim()) {
        body.bio = bio;
      }

      body.interests = [...activeInterests];

      btn.disabled = true;
      btn.textContent = '$ saving...';

      try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        const res = await fetch('/api/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
          body: JSON.stringify(body)
        });
        const data = await res.json();
        if (res.ok) {
          clearProfileError();
          btn.textContent = '$ saved ✓';
          document.getElementById('pwChangeFields').hidden = true;
          document.getElementById('changePwBtn').textContent = '$ change --password';
          document.getElementById('currentPassword').value = '';
          document.getElementById('newPassword').value = '';
          document.getElementById('confirmPassword').value = '';
          setTimeout(() => { btn.textContent = '$ save --apply'; btn.disabled = false; }, 2000);
        } else {
          showProfileError(data.error || '// save failed');
          btn.disabled = false;
          btn.textContent = '$ save --apply';
        }
      } catch (err) {
        showProfileError('// network failure');
        btn.disabled = false;
        btn.textContent = '$ save --apply';
      }
    });
