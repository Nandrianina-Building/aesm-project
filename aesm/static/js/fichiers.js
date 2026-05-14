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

// ── Filter logic (client-side for initial render, AJAX for dynamic) ──
const searchInput = document.getElementById("searchInput");
const categorySelect = document.getElementById("categorySelect");
const catPills = document.querySelectorAll(".cat-pill");
const fileContainer = document.getElementById("fileContainer");
const noResults = document.getElementById("noResults");

let selectedCat = "all";
let ajaxTimeout = null;

// Detect if server supports AJAX (has files loaded via Django)
const hasAjax = true; // set to false to use client-side only

// ── AJAX load ──
function loadFilesAjax() {
  const search = searchInput.value.trim();
  const category = selectedCat;

  fileContainer.innerHTML = `
        <div class="loading">
          <div class="spinner"></div> Chargement…
        </div>`;
  noResults.style.display = "none";

  fetch(`?search=${encodeURIComponent(search)}&category=${category}`, {
    headers: { "X-Requested-With": "XMLHttpRequest" },
  })
    .then((r) => r.json())
    .then((data) => {
      fileContainer.innerHTML = data.html || "";
      noResults.style.display =
        !fileContainer.children.length || fileContainer.innerHTML.trim() === ""
          ? "block"
          : "none";
    })
    .catch(() => {
      fileContainer.innerHTML =
        '<div class="empty-state"><i class="fa fa-circle-exclamation"></i><p>Erreur de chargement.</p></div>';
    });
}

// ── CLIENT-SIDE filter (fallback when AJAX not used) ──
function filterClientSide() {
  const q = searchInput.value.toLowerCase().trim();
  const cards = fileContainer.querySelectorAll(".file-card");
  let visible = 0;

  cards.forEach((card) => {
    const name = card.dataset.name || "";
    const desc = card.dataset.desc || "";
    const category = card.dataset.category || "";

    const matchSearch = !q || name.includes(q) || desc.includes(q);
    const matchCategory = selectedCat === "all" || category === selectedCat;

    if (matchSearch && matchCategory) {
      card.style.display = "flex";
      visible++;
    } else {
      card.style.display = "none";
    }
  });

  noResults.style.display = visible === 0 ? "block" : "none";
}

function triggerFilter() {
  clearTimeout(ajaxTimeout);
  ajaxTimeout = setTimeout(() => {
    if (hasAjax) loadFilesAjax();
    else filterClientSide();
  }, 280);
}

// ── Events ──
searchInput.addEventListener("input", triggerFilter);

catPills.forEach((pill) => {
  pill.addEventListener("click", () => {
    catPills.forEach((p) => p.classList.remove("active"));
    pill.classList.add("active");
    selectedCat = pill.dataset.id;
    categorySelect.value = selectedCat;
    triggerFilter();
  });
});

categorySelect.addEventListener("change", () => {
  selectedCat = categorySelect.value;
  catPills.forEach((p) => {
    p.classList.toggle("active", p.dataset.id === selectedCat);
  });
  triggerFilter();
});
