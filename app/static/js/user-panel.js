function openUserPanel(username) {
  const panel = document.getElementById('userPanel');
  const backdrop = document.getElementById('userPanelBackdrop');
  panel.classList.remove('active');
  backdrop.classList.add('active');
  fetch('/api/users/' + encodeURIComponent(username))
    .then(r => r.json())
    .then(data => {
      document.getElementById('userPanelAvatar').src = data.avatar;
      document.getElementById('userPanelUsername').textContent = data.username;
      document.getElementById('userPanelJoined').textContent = '// joined ' + data.joined;
      const bioSection = document.getElementById('userPanelBioSection');
      if (data.bio) {
        document.getElementById('userPanelBio').textContent = data.bio;
        bioSection.hidden = false;
      } else {
        bioSection.hidden = true;
      }
      const interestsEl = document.getElementById('userPanelInterests');
      const interestsSection = document.getElementById('userPanelInterestsSection');
      if (data.interests.length) {
        interestsEl.innerHTML = data.interests.map(i => `<span class="debate-tag">${i}</span>`).join('');
        interestsSection.hidden = false;
      } else {
        interestsSection.hidden = true;
      }
      panel.classList.add('active');
    });
}

function closeUserPanel() {
  document.getElementById('userPanel').classList.remove('active');
  document.getElementById('userPanelBackdrop').classList.remove('active');
}
