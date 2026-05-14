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

// Tabs
const tabBtns = document.querySelectorAll(".tab-btn");
const sections = document.querySelectorAll(".section");
tabBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    const cat = btn.dataset.cat;
    tabBtns.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    sections.forEach((s) =>
      s.classList.toggle("active", s.classList.contains(cat)),
    );
  });
});
