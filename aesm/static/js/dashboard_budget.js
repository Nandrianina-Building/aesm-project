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

// ── Tabs ──
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

// ── Chart.js defaults ──
Chart.defaults.font.family = "'DM Sans', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = "#6b7280";

const COLORS = [
  "#2d35c9",
  "#16a34a",
  "#f59e0b",
  "#dc2626",
  "#9333ea",
  "#0891b2",
  "#ea6e0e",
  "#6c6fff",
];

// ── Recettes par catégorie ──
let recettesData = [];
try {
  recettesData = JSON.parse(
    document.getElementById("recettes-data").textContent,
  );
} catch (e) {}

new Chart(document.getElementById("chartRecettes"), {
  type: "pie",
  data: {
    labels: recettesData.map((i) => i.categorie__nom),
    datasets: [
      {
        data: recettesData.map((i) => i.total),
        backgroundColor: COLORS,
        borderWidth: 2,
        borderColor: "#fff",
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "right",
        labels: { padding: 16, boxWidth: 12, font: { size: 12 } },
      },
    },
  },
});

// ── Dépenses par catégorie ──
let depensesData = [];
try {
  depensesData = JSON.parse(
    document.getElementById("depenses-data").textContent,
  );
} catch (e) {}

new Chart(document.getElementById("chartDepenses"), {
  type: "pie",
  data: {
    labels: depensesData.map((i) => i.categorie__nom),
    datasets: [
      {
        data: depensesData.map((i) => i.total),
        backgroundColor: [
          "#dc2626",
          "#f59e0b",
          "#ea6e0e",
          "#9333ea",
          "#6b7280",
          "#2d35c9",
        ],
        borderWidth: 2,
        borderColor: "#fff",
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "right",
        labels: { padding: 16, boxWidth: 12, font: { size: 12 } },
      },
    },
  },
});

// ── Évolution mensuelle (bar) ──
// Build from transactions data passed via Django template variable
const monthLabels = [
  "Jan",
  "Fév",
  "Mar",
  "Avr",
  "Mai",
  "Jun",
  "Jul",
  "Aoû",
  "Sep",
  "Oct",
  "Nov",
  "Déc",
];

// These arrays should ideally come from Django context
// Fallback: empty arrays (Django can inject via json_script if needed)
const recMensuelles = window.recettes_mensuelles || [
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];
const depMensuelles = window.depenses_mensuelles || [
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

new Chart(document.getElementById("chartEvolution"), {
  type: "bar",
  data: {
    labels: monthLabels,
    datasets: [
      {
        label: "Recettes",
        data: recMensuelles,
        backgroundColor: "#16a34a",
        borderRadius: 5,
      },
      {
        label: "Dépenses",
        data: depMensuelles,
        backgroundColor: "#dc2626",
        borderRadius: 5,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: "bottom", labels: { padding: 16, boxWidth: 12 } },
    },
    scales: {
      x: { grid: { display: false } },
      y: {
        grid: { color: "#f3f4f6" },
        ticks: { callback: (v) => v.toLocaleString() },
      },
    },
  },
});

// ── Tendance solde cumulé (line) ──
const soldeCumule = window.solde_cumule || [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];

new Chart(document.getElementById("chartSolde"), {
  type: "line",
  data: {
    labels: monthLabels,
    datasets: [
      {
        label: "Solde cumulé",
        data: soldeCumule,
        borderColor: "#2d35c9",
        backgroundColor: "rgba(45,53,201,0.08)",
        borderWidth: 2.5,
        pointBackgroundColor: "#2d35c9",
        pointRadius: 5,
        fill: true,
        tension: 0.3,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: "bottom", labels: { padding: 16, boxWidth: 12 } },
    },
    scales: {
      x: { grid: { display: false } },
      y: {
        grid: { color: "#f3f4f6" },
        ticks: { callback: (v) => v.toLocaleString() },
      },
    },
  },
});
