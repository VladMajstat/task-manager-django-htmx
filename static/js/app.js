// Confirm modal for HTMX actions (for example, delete).
(() => {
  const modal = document.getElementById("app-confirm");
  if (!modal) {
    return;
  }

  const body = document.getElementById("app-confirm-body");
  const okBtn = modal.querySelector("[data-confirm-ok]");
  const cancelEls = modal.querySelectorAll("[data-confirm-cancel]");

  let pending = null;

  // Close the modal and restore body state.
  const closeModal = () => {
    modal.hidden = true;
    document.body.classList.remove("app-modal-open");
  };

  // Open the modal and store the OK callback.
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

  // Intercept HTMX confirm and show the custom modal.
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

// Highlight tasks due "today/tomorrow".
(() => {
  const dueSoonClass = "app-task-due-soon";

  // Parse YYYY-MM-DD into a Date or return null.
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

  // Check if the deadline is not later than tomorrow.
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

  // Update due-soon highlighting within the given root.
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

// Remove the "No projects yet" message when cards exist.
(() => {
  // Hide empty-state when the grid has projects.
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

// Client-side form validation (required + date).
(() => {
  const requiredMessage = "This field is required.";
  const deadlineMessage = "Please choose today or a future date.";

  // Create a feedback node if it does not exist.
  const ensureFeedback = (field) => {
    let feedback = field.parentElement?.querySelector(".invalid-feedback");
    if (!feedback) {
      feedback = document.createElement("div");
      feedback.className = "invalid-feedback";
      field.parentElement?.appendChild(feedback);
    }
    return feedback;
  };

  // Validate one field and show/hide the error.
  const validateField = (field) => {
    if (field.disabled || field.type === "hidden") {
      return true;
    }
    const form = field.closest("form");
    const quietMode = form?.dataset.validate === "quiet";
    let isValid = true;
    let message = "";

    if (field.required && !field.value.trim()) {
      isValid = false;
      message = requiredMessage;
    }

    if (isValid && field.type === "date" && field.value) {
      const min = field.getAttribute("min");
      if (min && field.value < min) {
        isValid = false;
        message = deadlineMessage;
      }
    }

    if (quietMode) {
      field.classList.remove("is-invalid");
      const feedback = field.parentElement?.querySelector(".invalid-feedback");
      if (feedback) {
        feedback.textContent = "";
        feedback.style.display = "none";
      }
      return isValid;
    }
    field.classList.toggle("is-invalid", !isValid);
    if (!isValid) {
      const feedback = ensureFeedback(field);
      feedback.textContent = message;
      feedback.style.display = "block";
    } else {
      const feedback = field.parentElement?.querySelector(".invalid-feedback");
      if (feedback) {
        feedback.textContent = "";
        feedback.style.display = "none";
      }
    }
    return isValid;
  };

  // Validate all fields in a form.
  const validateForm = (form) => {
    const fields = form.querySelectorAll("input, textarea, select");
    let ok = true;
    fields.forEach((field) => {
      if (!validateField(field)) {
        ok = false;
      }
    });
    return ok;
  };

  // Attach live validation to forms within the root.
  const bindValidation = (root = document) => {
    root.querySelectorAll("form").forEach((form) => {
      if (form.dataset.liveValidated === "1") {
        return;
      }
      form.dataset.liveValidated = "1";

      form.addEventListener("input", (event) => {
        if (event.target instanceof HTMLElement) {
          validateField(event.target);
        }
      });

      form.addEventListener("blur", (event) => {
        if (event.target instanceof HTMLElement) {
          validateField(event.target);
        }
      }, true);

      form.addEventListener("submit", (event) => {
        if (!validateForm(form)) {
          event.preventDefault();
          event.stopPropagation();
        }
      });
    });
  };

  document.addEventListener("DOMContentLoaded", () => bindValidation());
  document.body.addEventListener("htmx:afterSwap", (event) => {
    bindValidation(event.target);
  });

  document.body.addEventListener("htmx:beforeRequest", (event) => {
    const form = event.target?.closest?.("form");
    if (!form || form.dataset.validate !== "quiet") {
      return;
    }
    if (!validateForm(form)) {
      event.preventDefault();
      event.stopPropagation();
    }
  });
})();
