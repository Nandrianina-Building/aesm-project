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

const searchInput = document.getElementById("search");
const catSelect = document.getElementById("catSelect");
const catPills = document.querySelectorAll(".cat-pill");
const noResults = document.getElementById("no-results");
let selectedCat = "all";

function filter() {
  const q = searchInput.value.toLowerCase().trim();
  let visible = 0;
  document.querySelectorAll(".pub-item").forEach((p) => {
    const match =
      (!q || p.dataset.title.includes(q) || p.dataset.content.includes(q)) &&
      (selectedCat === "all" || p.dataset.category === selectedCat);
    p.style.display = match ? "flex" : "none";
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
    catSelect.value = selectedCat;
    filter();
  });
});
catSelect.addEventListener("change", () => {
  selectedCat = catSelect.value;
  catPills.forEach((p) =>
    p.classList.toggle("active", p.dataset.id === selectedCat),
  );
  filter();
});
