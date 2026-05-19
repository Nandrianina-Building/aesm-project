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

// ── Soumission auto du formulaire ──
// Quand l'utilisateur tape dans la recherche → soumet après 400ms
// → retourne automatiquement à la page 1 (pas de page= dans l'URL)
const searchInput = document.getElementById("searchInput");
let searchTimer;
searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    document.getElementById("filterForm").submit();
  }, 400);
});

// Le select mobile soumet aussi immédiatement
document
  .getElementById("catSelectMobile")
  .addEventListener("change", function () {
    document.getElementById("catHidden").value = this.value;
    document.getElementById("filterForm").submit();
  });
