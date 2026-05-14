// ── Hamburger ──
const hamburger = document.getElementById("hamburger");
const mobileMenu = document.getElementById("mobileMenu");
hamburger.addEventListener("click", () => {
  hamburger.classList.toggle("open");
  mobileMenu.classList.toggle("open");
});
mobileMenu.querySelectorAll("a").forEach((l) =>
  l.addEventListener("click", () => {
    hamburger.classList.remove("open");
    mobileMenu.classList.remove("open");
  }),
);

// ── Filter ──
const searchInput = document.getElementById("searchInput");
const categorySelect = document.getElementById("categorySelect");
const catPills = document.querySelectorAll(".cat-pill");
const noResults = document.getElementById("noResults");
let selectedCat = "all";

function filter() {
  const q = searchInput.value.toLowerCase().trim();
  const cards = document.querySelectorAll(".file-card");
  let visible = 0;

  cards.forEach((card) => {
    const name = card.dataset.name || "";
    const desc = card.dataset.desc || "";
    const cat = card.dataset.category || "";
    const match =
      (!q || name.includes(q) || desc.includes(q)) &&
      (selectedCat === "all" || cat === selectedCat);
    card.style.display = match ? "flex" : "none";
    if (match) visible++;
  });

  noResults.style.display = visible === 0 ? "block" : "none";
}

searchInput.addEventListener("input", filter);

catPills.forEach((pill) => {
  pill.addEventListener("click", () => {
    catPills.forEach((p) => p.classList.remove("active"));
    pill.classList.add("active");
    selectedCat = pill.dataset.id;
    categorySelect.value = selectedCat;
    filter();
  });
});

categorySelect.addEventListener("change", () => {
  selectedCat = categorySelect.value;
  catPills.forEach((p) =>
    p.classList.toggle("active", p.dataset.id === selectedCat),
  );
  filter();
});
