(function () {
  const app = document.getElementById("debate-app");
  const debateId = app ? app.dataset.debateId : "";

  const state = {
    currentPath: [createPathEntry(null, "Loading debate...", null)],
    currentThread: {
      parentId: null,
      topic: "Loading debate...",
      yesComments: [],
      noComments: [],
    },
    composerSide: null,
    loading: false,
  };

  const elements = {
    level: document.getElementById("current-level"),
    currentPath: document.getElementById("current-path"),
    currentQuestion: document.getElementById("current-question"),
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

  function createPathEntry(parentId, topic, viaSide) {
    return { parentId, topic, viaSide };
  }

  function currentEntry() {
    return state.currentPath[state.currentPath.length - 1];
  }

  function normalizeThread(thread) {
    return {
      parentId: thread.parent_id,
      topic: thread.topic,
      yesComments: thread.yes_comments || [],
      noComments: thread.no_comments || [],
    };
  }

  async function fetchJson(url, options) {
    const response = await fetch(url, options);

    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || `Request failed with status ${response.status}`);
    }

    return response.json();
  }

  async function loadThread() {
    if (!debateId) {
      renderFatalError("Missing debate id.");
      return;
    }

    state.loading = true;
    renderLoading();

    const parentId = currentEntry().parentId === null ? "root" : currentEntry().parentId;

    try {
      const data = await fetchJson(`/api/debates/${debateId}/thread?parent_id=${encodeURIComponent(parentId)}`);
      state.currentThread = normalizeThread(data.thread);
      currentEntry().topic = state.currentThread.topic;
      render();
    } catch (error) {
      renderFatalError("Could not load comments.");
      console.error(error);
    } finally {
      state.loading = false;
    }
  }

  function renderLoading() {
    renderPath();
    renderTopic();
    elements.yesOptions.innerHTML = "";
    elements.noOptions.innerHTML = "";
    elements.yesOptions.appendChild(createEmptyState("Loading YES arguments..."));
    elements.noOptions.appendChild(createEmptyState("Loading NO arguments..."));
  }

  function renderFatalError(message) {
    state.currentThread = {
      parentId: currentEntry().parentId,
      topic: message,
      yesComments: [],
      noComments: [],
    };
    render();
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
    elements.currentQuestion.innerHTML = `${escapeHtml(state.currentThread.topic)} <span class="cursor" aria-hidden="true"></span>`;
  }

  function renderCommentColumn(side, target) {
    const comments = side === "yes" ? state.currentThread.yesComments : state.currentThread.noComments;
    target.innerHTML = "";

    if (!comments.length) {
      target.appendChild(createEmptyState(`No ${side.toUpperCase()} arguments yet.`));
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
    card.dataset.openId = String(comment.id);
    card.tabIndex = 0;
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", `Open branch from comment by ${comment.author}`);

    card.innerHTML = `
      <div class="comment-meta">[#${index + 1}] @${escapeHtml(comment.author)}</div>
      <p class="comment-text">"${escapeHtml(comment.text)}"</p>
      <div class="comment-footer">
        <button
          class="vote-button${comment.liked ? " is-liked" : ""}"
          type="button"
          data-like-id="${escapeHtml(comment.id)}"
          aria-pressed="${comment.liked ? "true" : "false"}"
          aria-label="Like this comment"
        >
          ${likeIcon()}
          <span>${comment.votes}</span>
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
    const allComments = [...state.currentThread.yesComments, ...state.currentThread.noComments];
    return allComments.find((comment) => String(comment.id) === String(commentId)) || null;
  }

  function openCommentBranch(commentId) {
    const comment = findCommentById(commentId);
    if (!comment) {
      return;
    }

    state.currentPath = [...state.currentPath, createPathEntry(comment.id, comment.text, comment.side)];
    closeComposer();
    loadThread();
  }

  async function toggleLike(commentId) {
    const comment = findCommentById(commentId);
    if (!comment) {
      return;
    }

    try {
      const data = await fetchJson(`/api/comments/${comment.id}/vote`, { method: "POST" });
      comment.liked = data.liked;
      comment.votes = data.upvote_count;
      render();
    } catch (error) {
      console.error(error);
    }
  }

  function openComposer(side) {
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
    if (!state.composerSide) {
      return;
    }

    const side = state.composerSide;
    const parentId = currentEntry().parentId;

    try {
      const data = await fetchJson(`/api/debates/${debateId}/comments`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          side,
          content: text,
          parent_id: parentId,
        }),
      });

      const comments = side === "yes" ? state.currentThread.yesComments : state.currentThread.noComments;
      comments.unshift(data.comment);
      closeComposer();
      render();
    } catch (error) {
      console.error(error);
    }
  }

  function escapeHtml(value) {
    return String(value ?? "")
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

  elements.composeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      openComposer(button.dataset.composeSide);
    });
  });

  elements.closeComposer.addEventListener("click", closeComposer);

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

    addComment(text);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !elements.composer.hidden) {
      closeComposer();
    }
  });

  loadThread();
})();
