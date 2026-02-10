const modal = document.getElementById("entryModal");
const modalTitle = document.getElementById("modalTitle");
const entryForm = document.getElementById("entryForm");
const titleInput = document.getElementById("title");

document.getElementById("addFromDetailsBtn").addEventListener("click", () => {
  modalTitle.textContent = "Add New Entry";
  entryForm.reset();

  // Prefill title from details page
  titleInput.value = window.ENTRY_DETAILS_CONFIG.title;

  modal.style.display = "block";
});

document.querySelectorAll(".close").forEach(el =>
  el.addEventListener("click", () => (modal.style.display = "none"))
);

window.addEventListener("click", e => {
  if (e.target === modal) modal.style.display = "none";
});