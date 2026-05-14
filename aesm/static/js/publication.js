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

// ── Filter logic ──
const searchInput = document.getElementById("search");
const catSelect = document.getElementById("catSelect");
const catPills = document.querySelectorAll(".cat-pill");
const pubs = document.querySelectorAll(".pub-item");
const noResults = document.getElementById("no-results");

let selectedCat = "all";

function filter() {
  const q = searchInput.value.toLowerCase().trim();
  let visible = 0;

  pubs.forEach((p) => {
    const title = p.dataset.title || "";
    const content = p.dataset.content || "";
    const category = p.dataset.category || "";

    const matchSearch = !q || title.includes(q) || content.includes(q);
    const matchCategory = selectedCat === "all" || category === selectedCat;

    if (matchSearch && matchCategory) {
      p.style.display = "flex";
      visible++;
    } else {
      p.style.display = "none";
    }
  });

  noResults.style.display = visible === 0 ? "block" : "none";
}

// Search input
searchInput.addEventListener("input", filter);

// Category pills (desktop)
catPills.forEach((pill) => {
  pill.addEventListener("click", () => {
    catPills.forEach((p) => p.classList.remove("active"));
    pill.classList.add("active");
    selectedCat = pill.dataset.id;
    catSelect.value = selectedCat;
    filter();
  });
});

// Category select (mobile)
catSelect.addEventListener("change", () => {
  selectedCat = catSelect.value;
  catPills.forEach((p) => {
    p.classList.toggle("active", p.dataset.id === selectedCat);
  });
  filter();
});
