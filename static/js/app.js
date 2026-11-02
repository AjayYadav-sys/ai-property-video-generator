(() => {
  const form = document.getElementById("listing-form");
  if (!form) return;

  const limits = window.APP_LIMITS || { minImages: 4, maxImages: 8, maxImageBytes: 10 * 1024 * 1024 };
  const input = document.getElementById("image-input");
  const dropZone = document.getElementById("drop-zone");
  const grid = document.getElementById("preview-grid");
  const counter = document.getElementById("image-counter");
  const errorBox = document.getElementById("form-errors");
  const submitBtn = document.getElementById("submit-btn");

  const allowed = ["image/jpeg", "image/png", "image/webp"];
  let files = [];
  let dragIndex = null;

  function showErrors(messages) {
    errorBox.innerHTML = "";
    if (!messages.length) {
      errorBox.classList.add("is-hidden");
      return;
    }
    messages.forEach((text) => {
      const p = document.createElement("p");
      p.textContent = text;
      errorBox.appendChild(p);
    });
    errorBox.classList.remove("is-hidden");
  }

  function flattenServerErrors(errors) {
    return Object.values(errors || {}).flat();
  }

  function clientMessages() {
    const messages = [];
    const title = form.title.value.trim();
    const location = form.location.value.trim();
    if (!title) messages.push("Property title is required.");
    if (!location) messages.push("Location is required.");
    if (files.length < limits.minImages) {
      messages.push(`Upload at least ${limits.minImages} property images (you selected ${files.length}).`);
    }
    if (files.length > limits.maxImages) {
      messages.push(`Upload at most ${limits.maxImages} property images.`);
    }
    return messages;
  }

  function render() {
    grid.innerHTML = "";
    files.forEach((file, index) => {
      const card = document.createElement("figure");
      card.className = "preview-card";
      card.draggable = true;
      card.dataset.index = String(index);

      const img = document.createElement("img");
      img.alt = `Preview ${index + 1}`;
      img.src = URL.createObjectURL(file);
      img.onload = () => URL.revokeObjectURL(img.src);

      const meta = document.createElement("div");
      meta.className = "meta";
      meta.textContent = `${index + 1}. ${file.name}`;

      const remove = document.createElement("button");
      remove.type = "button";
      remove.setAttribute("aria-label", `Remove ${file.name}`);
      remove.textContent = "×";
      remove.addEventListener("click", () => {
        files.splice(index, 1);
        render();
      });

      card.addEventListener("dragstart", () => {
        dragIndex = index;
      });
      card.addEventListener("dragover", (event) => {
        event.preventDefault();
      });
      card.addEventListener("drop", (event) => {
        event.preventDefault();
        const target = Number(card.dataset.index);
        if (dragIndex === null || target === dragIndex) return;
        const moved = files.splice(dragIndex, 1)[0];
        files.splice(target, 0, moved);
        dragIndex = null;
        render();
      });

      card.append(img, meta, remove);
      grid.appendChild(card);
    });

    const ready = files.length >= limits.minImages && files.length <= limits.maxImages;
    counter.textContent = `${files.length} / ${limits.minImages} minimum · ${limits.maxImages} max`;
    counter.style.color = ready ? "#7dce82" : "";
    submitBtn.disabled = files.length < limits.minImages;
  }

  function addFiles(list) {
    const messages = [];
    Array.from(list || []).forEach((file) => {
      if (!allowed.includes(file.type) && !/\.(jpe?g|png|webp)$/i.test(file.name)) {
        messages.push(`${file.name} must be JPG, PNG, or WebP.`);
        return;
      }
      if (file.size > limits.maxImageBytes) {
        messages.push(`${file.name} is larger than 10 MB.`);
        return;
      }
      if (files.length >= limits.maxImages) {
        messages.push(`Only ${limits.maxImages} images are allowed.`);
        return;
      }
      files.push(file);
    });
    input.value = "";
    showErrors(messages);
    render();
  }

  input.addEventListener("change", (event) => addFiles(event.target.files));

  ["dragenter", "dragover"].forEach((name) => {
    dropZone.addEventListener(name, (event) => {
      event.preventDefault();
      dropZone.classList.add("is-dragover");
    });
  });
  ["dragleave", "drop"].forEach((name) => {
    dropZone.addEventListener(name, () => dropZone.classList.remove("is-dragover"));
  });
  dropZone.addEventListener("drop", (event) => {
    event.preventDefault();
    addFiles(event.dataTransfer.files);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const messages = clientMessages();
    if (messages.length) {
      showErrors(messages);
      return;
    }

    const payload = new FormData();
    new FormData(form).forEach((value, key) => {
      if (key !== "images") payload.append(key, value);
    });
    files.forEach((file) => payload.append("images", file, file.name));

    submitBtn.disabled = true;
    submitBtn.textContent = "Saving job…";

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: payload,
        headers: { Accept: "application/json", "X-Requested-With": "XMLHttpRequest" },
      });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        showErrors(flattenServerErrors(data.errors) || ["Could not save this listing."]);
        submitBtn.disabled = false;
        submitBtn.textContent = "Save listing job";
        return;
      }
      window.location.href = data.redirect;
    } catch (error) {
      showErrors(["Network error. Check that the Flask server is running."]);
      submitBtn.disabled = false;
      submitBtn.textContent = "Save listing job";
    }
  });

  render();
})();
