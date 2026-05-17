(function () {
  const app = document.getElementById("debate-app");
  if (!app) {
    return;
  }

  const debateId = app.dataset.debateId;
  const initialTopic = app.dataset.debateTitle || "Debate";
  const isAuthenticated = app.dataset.authenticated === "true";
  const loginUrl = app.dataset.loginUrl || "/login";
  const DEFAULT_AVATAR_URL = "/static/images/avatars/robot.svg";
  const REFRESH_INTERVAL_MS = 3000;

  const state = {
    currentPath: [{ id: "root", topic: initialTopic, author: "", authorAvatar: "", viaSide: null }],
    comments: { yes: [], no: [] },
    composerSide: null,
    isLoading: false,
    refreshTimer: null,
  };

  const elements = {
    level: document.getElementById("current-level"),
    currentPath: document.getElementById("current-path"),
    currentQuestion: document.getElementById("current-question"),
    topicAuthor: document.getElementById("topic-author"),
    yesOptions: document.getElementById("yes-options"),
    noOptions: document.getElementById("no-options"),
    composer: document.getElementById("comment-composer"),
    composerTitle: document.getElementById("composer-title"),
    composerHint: document.getElementById("composer-hint"),
    commentForm: document.getElementById("comment-form"),
    commentInput: document.getElementById("comment-input"),
    closeComposer: document.getElementById("close-composer"),
    composeButtons: Array.from(document.querySelectorAll("[data-compose-side]")),
  };

  function currentEntry() {
    return state.currentPath[state.currentPath.length - 1];
  }

  function currentParentId() {
    return currentEntry().id || "root";
  }

  function threadUrl(parentId) {
    return `/api/debates/${encodeURIComponent(debateId)}/thread?parent_id=${encodeURIComponent(parentId || "root")}`;
  }

  async function requestJson(url, options = {}) {
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const method = (options.method || 'GET').toUpperCase();
    const headers = { "Content-Type": "application/json" };
    if (method !== 'GET' && method !== 'HEAD' && csrfMeta) {
      headers['X-CSRFToken'] = csrfMeta.content;
    }
    const response = await fetch(url, {
      headers,
      ...options,
    });

    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(payload.error || "request failed");
      if (response.status === 401) {
        error.redirectedToLogin = true;
        redirectToLogin();
      }
      throw error;
    }

    return payload;
  }

  function redirectToLogin() {
    window.location.assign(loginUrl);
  }

  function requireLogin() {
    if (isAuthenticated) {
      return true;
    }

    redirectToLogin();
    return false;
  }

  async function loadThread(options = {}) {
    if (!debateId || state.isLoading) {
      return;
    }

    state.isLoading = true;
    try {
      const payload = await requestJson(threadUrl(currentParentId()));
      const topic = payload.topic || {};
      currentEntry().topic = topic.text || currentEntry().topic;
      currentEntry().author = topic.author || currentEntry().author;
      currentEntry().authorAvatar = topic.author_avatar || currentEntry().authorAvatar;
      state.comments = payload.comments || { yes: [], no: [] };
      render();
    } catch (error) {
      if (!options.silent) {
        renderError(error.message);
      }
    } finally {
      state.isLoading = false;
    }
  }

  function renderError(message) {
    const fallback = createEmptyState(`Unable to load debate data: ${message}`);
    elements.yesOptions.innerHTML = "";
    elements.noOptions.innerHTML = "";
    elements.yesOptions.appendChild(fallback);
  }

  function renderPath() {
    elements.level.textContent = String(state.currentPath.length);
    elements.currentPath.innerHTML = "";

    state.currentPath.forEach((entry, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "path-card";

      if (index === state.currentPath.length - 1) {
        button.classList.add("is-current");
      }

      if (entry.viaSide === "yes") {
        button.classList.add("is-yes-branch");
      }

      if (entry.viaSide === "no") {
        button.classList.add("is-no-branch");
      }

      button.innerHTML = `
        <span class="path-meta">
          <span class="path-step">step_${index + 1}</span>
          ${pathBadge(entry.viaSide, index)}
        </span>
        <span class="path-question">${escapeHtml(entry.topic)}</span>
      `;

      button.addEventListener("click", () => {
        state.currentPath = state.currentPath.slice(0, index + 1);
        closeComposer();
        loadThread();
      });

      elements.currentPath.appendChild(button);
    });
  }

  function renderTopic() {
    const entry = currentEntry();
    elements.currentQuestion.innerHTML = `${escapeHtml(entry.topic)} <span class="cursor" aria-hidden="true"></span>`;

    if (!elements.topicAuthor) {
      return;
    }

    if (!entry.author) {
      elements.topicAuthor.hidden = true;
      elements.topicAuthor.removeAttribute("data-username");
      elements.topicAuthor.innerHTML = "";
      return;
    }

    elements.topicAuthor.hidden = false;
    elements.topicAuthor.dataset.username = entry.author;
    elements.topicAuthor.setAttribute("aria-label", `Open profile for ${entry.author}`);
    elements.topicAuthor.innerHTML = "";

    const avatar = document.createElement("img");
    avatar.className = "topic-author-avatar";
    avatar.src = entry.authorAvatar || DEFAULT_AVATAR_URL;
    avatar.alt = "";
    avatar.setAttribute("aria-hidden", "true");

    const name = document.createElement("span");
    name.className = "topic-author-name";
    name.textContent = `@${entry.author}`;

    elements.topicAuthor.append(avatar, name);
  }

  function renderCommentColumn(side, target) {
    const comments = state.comments[side] || [];
    target.innerHTML = "";

    if (!comments.length) {
      target.appendChild(createEmptyState("No comments on this side yet."));
      return;
    }

    comments.forEach((comment, index) => {
      target.appendChild(createCommentCard(comment, index));
    });
  }

  function createCommentCard(comment, index) {
    const card = document.createElement("article");
    card.className = "comment-option";
    card.classList.add(comment.side === "yes" ? "is-yes" : "is-no");
    card.dataset.openId = comment.id;
    card.tabIndex = 0;
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", `Open branch from comment by ${comment.author}`);

    card.innerHTML = `
      <div class="comment-meta">[#${index + 1}] @${escapeHtml(comment.author)}</div>
      <p class="comment-text">"${escapeHtml(comment.content)}"</p>
      <div class="comment-footer">
        <button
          class="vote-button${comment.liked ? " is-liked" : ""}"
          type="button"
          data-like-id="${escapeHtml(String(comment.id))}"
          aria-pressed="${comment.liked ? "true" : "false"}"
          aria-label="Like this comment"
        >
          ${likeIcon()}
          <span>${comment.upvote_count}</span>
        </button>
      </div>
    `;

    return card;
  }

  function createEmptyState(text) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = text;
    return empty;
  }

  function findCommentById(commentId) {
    const id = Number(commentId);
    return [...(state.comments.yes || []), ...(state.comments.no || [])]
      .find((comment) => comment.id === id) || null;
  }

  async function openCommentBranch(commentId) {
    const comment = findCommentById(commentId);
    if (!comment) {
      return;
    }

    state.currentPath = [
      ...state.currentPath,
      {
        id: comment.id,
        topic: comment.content,
        author: comment.author,
        authorAvatar: comment.author_avatar || "",
        viaSide: comment.side,
      },
    ];
    closeComposer();
    await loadThread();
  }

  async function toggleLike(commentId) {
    if (!requireLogin()) {
      return;
    }

    const comment = findCommentById(commentId);
    if (!comment) {
      return;
    }

    try {
      const payload = await requestJson(`/api/comments/${encodeURIComponent(comment.id)}/vote`, {
        method: "POST",
      });
      comment.liked = payload.liked;
      comment.upvote_count = payload.upvote_count;
      render();
      await new Promise((resolve) => setTimeout(resolve, 350));
      await loadThread({ silent: true });
    } catch (error) {
      if (!error.redirectedToLogin) {
        alert(error.message);
      }
    }
  }

  function openComposer(side) {
    if (!requireLogin()) {
      return;
    }

    state.composerSide = side;
    elements.composer.hidden = false;
    elements.composer.classList.toggle("is-yes", side === "yes");
    elements.composer.classList.toggle("is-no", side === "no");
    elements.composerTitle.textContent = `$ add-comment --${side}`;
    elements.composerHint.textContent = side === "yes"
      ? "// Write your YES-side argument"
      : "// Write your NO-side argument";

    elements.composer.scrollIntoView({ behavior: "smooth", block: "nearest" });

    requestAnimationFrame(() => {
      elements.commentInput.focus();
    });
  }

  function closeComposer() {
    state.composerSide = null;
    elements.composer.hidden = true;
    elements.composer.classList.remove("is-yes", "is-no");
    elements.commentForm.reset();
  }

  async function addComment(text) {
    if (!requireLogin()) {
      return;
    }

    if (!state.composerSide) {
      return;
    }

    try {
      await requestJson(`/api/debates/${encodeURIComponent(debateId)}/comments`, {
        method: "POST",
        body: JSON.stringify({
          parent_id: currentParentId(),
          side: state.composerSide,
          content: text,
        }),
      });
      closeComposer();
      await loadThread();
    } catch (error) {
      if (!error.redirectedToLogin) {
        alert(error.message);
      }
    }
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function likeIcon() {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M7 11v9"></path>
        <path d="M11 21h6.2a2 2 0 0 0 1.96-1.6l1.1-5.4a2 2 0 0 0-1.96-2.4H14V7.6A2.6 2.6 0 0 0 11.4 5l-3 6H5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h6Z"></path>
      </svg>
    `;
  }

  function pathBadge(viaSide, index) {
    if (index === 0) {
      return '<span class="path-badge path-badge-root">ROOT</span>';
    }

    if (viaSide === "yes") {
      return '<span class="path-badge path-badge-yes">[Y] YES</span>';
    }

    if (viaSide === "no") {
      return '<span class="path-badge path-badge-no">[N] NO</span>';
    }

    return "";
  }

  function handleCommentActivation(event, container) {
    const likeButton = event.target.closest("[data-like-id]");
    if (likeButton && container.contains(likeButton)) {
      event.stopPropagation();
      toggleLike(likeButton.dataset.likeId);
      return;
    }

    const card = event.target.closest("[data-open-id]");
    if (!card || !container.contains(card)) {
      return;
    }

    openCommentBranch(card.dataset.openId);
  }

  function render() {
    renderPath();
    renderTopic();
    renderCommentColumn("yes", elements.yesOptions);
    renderCommentColumn("no", elements.noOptions);
  }

  function startPolling() {
    if (state.refreshTimer) {
      clearInterval(state.refreshTimer);
    }

    state.refreshTimer = setInterval(() => {
      if (document.hidden || !elements.composer.hidden) {
        return;
      }
      loadThread({ silent: true });
    }, REFRESH_INTERVAL_MS);
  }

  elements.composeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      openComposer(button.dataset.composeSide);
    });
  });

  elements.closeComposer.addEventListener("click", closeComposer);

  if (elements.topicAuthor) {
    elements.topicAuthor.addEventListener("click", () => {
      const username = elements.topicAuthor.dataset.username;
      if (username && typeof window.openUserPanel === "function") {
        window.openUserPanel(username);
      }
    });
  }

  [elements.yesOptions, elements.noOptions].forEach((container) => {
    container.addEventListener("click", (event) => {
      handleCommentActivation(event, container);
    });

    container.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") {
        return;
      }

      if (event.target.closest("[data-like-id]")) {
        return;
      }

      const card = event.target.closest("[data-open-id]");
      if (!card || !container.contains(card)) {
        return;
      }

      event.preventDefault();
      openCommentBranch(card.dataset.openId);
    });
  });

  elements.commentForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const text = elements.commentInput.value.trim();
    if (!text) {
      return;
    }

    const submitBtn = elements.commentForm.querySelector('[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;
    addComment(text).finally(() => {
      if (submitBtn) submitBtn.disabled = false;
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !elements.composer.hidden) {
      closeComposer();
    }
  });

  render();
  loadThread();
  startPolling();
})();
