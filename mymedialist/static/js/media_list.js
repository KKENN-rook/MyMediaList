// Tab switching logic 
const tabs = document.querySelectorAll(".tab");
const rows = document.querySelectorAll("tbody tr");

tabs.forEach(tab => {
    tab.addEventListener("click", () => {
        tabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        const status = tab.dataset.status;
        rows.forEach(r => {
            r.style.display = (status === "All" || r.dataset.status === status) ? "" : "none";
        });
    });
});

// ------------ ADD/EDIT/DELETE MODAL ------------ 
const modal = document.getElementById("entryModal");
const modalTitle = document.getElementById("modalTitle");
const entryForm = document.getElementById("entryForm");
const saveBtn = document.getElementById("saveBtn");
const deleteBtn = document.getElementById("deleteBtn");
const { editUrl, deleteUrl, addUrl } = window.MEDIA_LIST_CONFIG;

// Add mode
document.getElementById("addEntryBtn").addEventListener("click", () => {
    modalTitle.textContent = "Add New Entry";
    entryForm.action = addUrl;
    saveBtn.textContent = "Add Entry";
    deleteBtn.style.display = "none";
    entryForm.reset();
    modal.style.display = "block";
});

// Edit mode
document.querySelectorAll(".edit-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        modalTitle.textContent = "Edit Entry";
        saveBtn.textContent = "Save Changes";
        deleteBtn.style.display = "inline-block";
        const entryId = btn.dataset.entryId;
        entryForm.action = editUrl + entryId; 

        // Fill fields 
        document.getElementById("entryId").value = entryId;  // Hidden field, used to assist in deleting correct entry
        document.getElementById("title").value = btn.dataset.title;
        document.getElementById("rating").value = btn.dataset.rating || "";
        document.getElementById("status").value = btn.dataset.status;
        document.getElementById("notes").value = btn.dataset.notes || "";
        // document.getElementById("progress_value").value = btn.dataset.progress || "";

        modal.style.display = "block";
    });
});

// Close modal
document.querySelectorAll(".close").forEach(el => el.addEventListener("click", () => {
    modal.style.display = "none";
}));

// Confirm delete
deleteBtn.addEventListener("click", () => {
    if (confirm("Are you sure you want to delete this entry?")) {
        const entryId = document.getElementById("entryId").value;
        entryForm.action = deleteUrl + entryId;
        entryForm.submit();
    }
});

// Close on click outside modal
window.addEventListener("click", e => {
    if (e.target === modal) modal.style.display = "none";
});


// ------------ SORTING LOGIC ------------ 
const sortSelect = document.getElementById("sortSelect");
const tbody = document.querySelector(".media-table tbody");

sortSelect.addEventListener("change", () => {
    const option = sortSelect.value;
    const rows = Array.from(tbody.querySelectorAll("tr"));

    let sorted;
    if (option === "title") {
        sorted = rows.sort((a, b) => {
            const titleA = a.querySelector(".title-text").textContent.trim().toLowerCase();
            const titleB = b.querySelector(".title-text").textContent.trim().toLowerCase();
            return titleA.localeCompare(titleB);
        });
    } else if (option === "rating") {
        sorted = rows.sort((a, b) => {
            const ratingA = parseFloat(a.children[1].textContent) || 0;
            const ratingB = parseFloat(b.children[1].textContent) || 0;
            return ratingB - ratingA; // high → low
        });
    }

    tbody.innerHTML = "";
    sorted.forEach(row => tbody.appendChild(row));
});