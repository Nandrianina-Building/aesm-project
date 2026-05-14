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

// ── Tab switching ──
const tabBtns = document.querySelectorAll(".tab-btn");
const sections = document.querySelectorAll(".section");
tabBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    const cat = btn.dataset.cat;
    tabBtns.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    sections.forEach((s) => {
      s.classList.toggle("active", s.classList.contains(cat));
    });
  });
});

// ── Accordion: Steps ──
document.querySelectorAll(".step-header").forEach((header) => {
  header.addEventListener("click", () => {
    const card = header.parentElement;
    // Close all others
    document.querySelectorAll(".step-card").forEach((c) => {
      if (c !== card) c.classList.remove("open");
    });
    card.classList.toggle("open");
  });
});

// ── Accordion: FAQ ──
document.querySelectorAll(".faq-question").forEach((q) => {
  q.addEventListener("click", () => {
    const item = q.parentElement;
    // Close all others
    document.querySelectorAll(".faq-item").forEach((i) => {
      if (i !== item) i.classList.remove("open");
    });
    item.classList.toggle("open");
  });
});
