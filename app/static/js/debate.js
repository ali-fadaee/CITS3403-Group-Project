(function () {
  const authorPools = {
    yes: ["tech_optimist", "ml_engineer", "startup_dev", "systems_researcher", "qa_lead", "logic_fan"],
    no: ["senior_dev", "architect_jane", "code_reviewer", "risk_analyst", "product_owner", "sec_engineer"],
  };

  const votesBySide = {
    yes: [42, 38, 29, 24, 18, 13],
    no: [45, 33, 27, 21, 17, 12],
  };

  const rootThread = {
    id: "root",
    topic: "Should AI replace human developers?",
    yesComments: [
      createComment("root-y1", "yes", "tech_optimist", "AI can analyze codebases faster and find patterns humans miss. This leads to more consistent quality.", 42),
      createComment("root-y2", "yes", "ml_engineer", "Studies show AI-assisted code has 40% fewer bugs. The data does not lie.", 38),
      createComment("root-y3", "yes", "startup_dev", "I have been using Copilot for 6 months. My productivity doubled and code quality improved.", 29),
    ],
    noComments: [
      createComment("root-n1", "no", "senior_dev", "AI does not understand context or business requirements. It just pattern matches.", 45),
      createComment("root-n2", "no", "architect_jane", "Human intuition and experience are irreplaceable for complex system design.", 33),
      createComment("root-n3", "no", "code_reviewer", "AI suggestions often introduce subtle bugs that only experienced devs catch.", 27),
    ],
  };

  const state = {
    currentPath: [createPathEntry(rootThread, null)],
    composerSide: null,
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

  function createComment(id, side, author, text, votes) {
    return { id, side, author, text, votes, liked: false, next: null };
  }

  function createPathEntry(thread, viaSide) {
    return { thread, viaSide };
  }

  function currentThread() {
    return state.currentPath[state.currentPath.length - 1].thread;
  }

  function getCommentsForSide(thread, side) {
    return side === "yes" ? thread.yesComments : thread.noComments;
  }

  function ensureNextThread(comment) {
    if (comment.next) {
      return comment.next;
    }

    comment.next = buildThreadFromComment(comment, state.currentPath.length + 1);
    return comment.next;
  }

  function buildThreadFromComment(comment, depth) {
    const seed = hashString(`${comment.id}:${comment.text}:${depth}`);

    return {
      id: `${comment.id}-thread-${depth}`,
      topic: comment.text,
      yesComments: buildGeneratedComments("yes", comment.text, depth, seed),
      noComments: buildGeneratedComments("no", comment.text, depth, seed + 17),
    };
  }

  function buildGeneratedComments(side, topic, depth, seed) {
    const templates = side === "yes"
      ? [
          'That point becomes stronger if we focus on implementation detail: "%s"',
          'The supporting case here is that "%s" already happens in practice.',
          'A fair extension of this argument is "%s" at scale.',
        ]
      : [
          'The main weakness in that argument is "%s" under real constraints.',
          'A strong counterpoint is that "%s" ignores edge cases.',
          'That statement falls apart once "%s" meets production reality.',
        ];

    const snippet = compactTopic(topic);

    return templates.map((template, index) => {
      const authorPool = authorPools[side];
      const votesPool = votesBySide[side];
      const author = authorPool[(seed + index) % authorPool.length];
      const votes = Math.max(3, votesPool[(seed + index) % votesPool.length] - depth * 2 + index);

      return createComment(
        `${side}-${seed}-${depth}-${index}`,
        side,
        author,
        template.replace("%s", snippet),
        votes
      );
    });
  }

  function compactTopic(topic) {
    const trimmed = topic.replace(/\s+/g, " ").trim();
    return trimmed.length > 118 ? `${trimmed.slice(0, 115)}...` : trimmed;
  }

  function hashString(value) {
    let hash = 0;
    for (let index = 0; index < value.length; index += 1) {
      hash = (hash * 31 + value.charCodeAt(index)) >>> 0;
    }
    return hash;
  }

  function renderPath() {
    elements.level.textContent = String(state.currentPath.length);
    elements.currentPath.innerHTML = "";

    state.currentPath.forEach((entry, index) => {
      const thread = entry.thread;
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
        <span class="path-question">${escapeHtml(thread.topic)}</span>
      `;

      button.addEventListener("click", () => {
        state.currentPath = state.currentPath.slice(0, index + 1);
        render();
      });

      elements.currentPath.appendChild(button);
    });
  }

  function renderTopic() {
    elements.currentQuestion.innerHTML = `${escapeHtml(currentThread().topic)} <span class="cursor" aria-hidden="true"></span>`;
  }

  function renderCommentColumn(side, target) {
    const comments = getCommentsForSide(currentThread(), side);
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

  function findCommentById(thread, commentId) {
    const allComments = [...thread.yesComments, ...thread.noComments];
    return allComments.find((comment) => comment.id === commentId) || null;
  }

  function openCommentBranch(commentId) {
    const comment = findCommentById(currentThread(), commentId);
    if (!comment) {
      return;
    }

    state.currentPath = [...state.currentPath, createPathEntry(ensureNextThread(comment), comment.side)];
    closeComposer();
    render();
  }

  function toggleLike(commentId) {
    const comment = findCommentById(currentThread(), commentId);
    if (!comment) {
      return;
    }

    comment.liked = !comment.liked;
    comment.votes += comment.liked ? 1 : -1;
    render();
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

  function addComment(text) {
    if (!state.composerSide) {
      return;
    }

    const side = state.composerSide;
    const comment = createComment(
      `${currentThread().id}-${side}-${Date.now()}`,
      side,
      "user_dev",
      text,
      0
    );

    getCommentsForSide(currentThread(), side).unshift(comment);
    closeComposer();
    render();
  }

  function escapeHtml(value) {
    return value
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

  render();
})();