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
