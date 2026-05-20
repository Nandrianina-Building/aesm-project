// Hamburger
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

// Recherche auto-submit après 400ms — retour page 1 automatique
const searchInput = document.getElementById("searchInput");
let searchTimer;
searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    document.getElementById("filterForm").submit();
  }, 800);
});

// Select mobile → submit immédiat
document
  .getElementById("catSelectMobile")
  .addEventListener("change", function () {
    document.getElementById("catHidden").value = this.value;
    document.getElementById("filterForm").submit();
  });
