const openBtn = document.getElementById("openModal");
const cancelBtn = document.getElementById("cancelModal");
const overlay = document.getElementById("modalOverlay");

openBtn.addEventListener("click", () => overlay.classList.add("open"));
cancelBtn.addEventListener("click", () => overlay.classList.remove("open"));
overlay.addEventListener("click", (e) => {
  if (e.target === overlay) overlay.classList.remove("open");
});
