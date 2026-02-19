const modal = document.getElementById("entryModal");
const modalTitle = document.getElementById("modalTitle");
const entryForm = document.getElementById("entryForm");
const titleInput = document.getElementById("title");
const statusInput = document.getElementById("status");
const progressInput = document.getElementById("progress_value"); // may be null
const ratingInput = document.getElementById("rating");
const notesInput = document.getElementById("notes");
const saveBtn = document.getElementById("saveBtn");

const config = JSON.parse(document.getElementById("entry-details-config").textContent);

const editBtn = document.getElementById("editFromDetailsBtn");
if (editBtn) editBtn.addEventListener("click", openEditModal);

const addBtn = document.getElementById("addFromDetailsBtn");
if (addBtn) addBtn.addEventListener("click", openAddModal);

function openAddModal() {
  modalTitle.textContent = "Add New Entry";
  entryForm.action = `/add/${config.category}`;
  entryForm.reset();

  titleInput.value = config.title;
  saveBtn.textContent = "Add Entry";

  // If progress exists, clear it explicitly
  if (progressInput) progressInput.value = "";

  // Enable API fields for add mode
  document.getElementById("sourceField").disabled = false;
  document.getElementById("external_idField").disabled = false;
  document.getElementById("total_unitsField").disabled = false;
  document.getElementById("unit_typeField").disabled = false;

  modal.style.display = "block";
}

function openEditModal() {
  modalTitle.textContent = "Edit Entry";
  entryForm.action = `/edit/${config.category}/${config.userEntryId}`;

  titleInput.value = config.userEntryData.title;
  statusInput.value = config.userEntryData.status;

  // Progress is optional now
  if (progressInput) {
    progressInput.value = config.userEntryData.progress_value ?? "";
  }

  ratingInput.value = config.userEntryData.rating ?? "";
  notesInput.value = config.userEntryData.notes ?? "";
  saveBtn.textContent = "Update Entry";

  // Disable API fields for edit mode
  document.getElementById("sourceField").disabled = true;
  document.getElementById("external_idField").disabled = true;
  document.getElementById("total_unitsField").disabled = true;
  document.getElementById("unit_typeField").disabled = true;

  modal.style.display = "block";
}

document.querySelectorAll(".close").forEach((el) =>
  el.addEventListener("click", () => (modal.style.display = "none"))
);

window.addEventListener("click", (e) => {
  if (e.target === modal) modal.style.display = "none";
});