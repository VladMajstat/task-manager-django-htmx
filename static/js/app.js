(() => {
  const modal = document.getElementById("app-confirm");
  if (!modal) {
    return;
  }

  const body = document.getElementById("app-confirm-body");
  const okBtn = modal.querySelector("[data-confirm-ok]");
  const cancelEls = modal.querySelectorAll("[data-confirm-cancel]");

  let pending = null;

  const closeModal = () => {
    modal.hidden = true;
    document.body.classList.remove("app-modal-open");
  };

  const openModal = (message, onConfirm) => {
    body.textContent = message || "Are you sure?";
    pending = onConfirm;
    modal.hidden = false;
    document.body.classList.add("app-modal-open");
  };

  okBtn.addEventListener("click", () => {
    const run = pending;
    closeModal();
    pending = null;
    if (run) {
      run();
    }
  });

  cancelEls.forEach((el) => {
    el.addEventListener("click", () => {
      pending = null;
      closeModal();
    });
  });

  const confirmHandler = (event) => {
    if (!event.detail || typeof event.detail.issueRequest !== "function") {
      return;
    }
    const source = event.detail.elt;
    if (!source || !source.matches("[data-confirm='delete']")) {
      return;
    }
    event.preventDefault();
    openModal(event.detail.question, () => event.detail.issueRequest(true));
  };

  document.body.addEventListener("htmx:confirm", confirmHandler);
  if (window.htmx && typeof window.htmx.on === "function") {
    window.htmx.on("htmx:confirm", confirmHandler);
  }
})();

(() => {
  const dueSoonClass = "app-task-due-soon";

  const parseDate = (value) => {
    if (!value) {
      return null;
    }
    const parts = value.split("-");
    if (parts.length !== 3) {
      return null;
    }
    const year = Number(parts[0]);
    const month = Number(parts[1]);
    const day = Number(parts[2]);
    if (!Number.isFinite(year) || !Number.isFinite(month) || !Number.isFinite(day)) {
      return null;
    }
    return new Date(year, month - 1, day);
  };

  const isDueSoon = (deadline) => {
    if (!deadline) {
      return false;
    }
    const today = new Date();
    const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const cutoff = new Date(todayStart);
    cutoff.setDate(todayStart.getDate() + 1);
    return deadline <= cutoff;
  };

  const updateDueSoon = (root = document) => {
    const rows = root.querySelectorAll(".app-task-row[data-deadline]");
    rows.forEach((row) => {
      const done = row.dataset.done === "1";
      const deadline = parseDate(row.dataset.deadline);
      const shouldHighlight = !done && isDueSoon(deadline);
      row.classList.toggle(dueSoonClass, shouldHighlight);
    });
  };

  document.addEventListener("DOMContentLoaded", () => updateDueSoon());
  document.body.addEventListener("htmx:afterSwap", (event) => {
    updateDueSoon(event.target);
  });
})();

(() => {
  const updateProjectsEmpty = () => {
    const grid = document.getElementById("projects-grid");
    if (!grid) {
      return;
    }
    const hasProjects = Boolean(grid.querySelector(".app-card"));
    const empty = document.getElementById("projects-empty");
    if (hasProjects && empty) {
      empty.remove();
    }
  };

  document.addEventListener("DOMContentLoaded", updateProjectsEmpty);
  document.body.addEventListener("htmx:afterSwap", updateProjectsEmpty);
})();
