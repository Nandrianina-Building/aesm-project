// Toggle password visibility
document.querySelectorAll(".toggle-pw").forEach((btn) => {
  btn.addEventListener("click", () => {
    const input = document.getElementById(btn.dataset.target);
    const icon = btn.querySelector("i");
    if (input.type === "password") {
      input.type = "text";
      icon.classList.replace("fa-eye", "fa-eye-slash");
    } else {
      input.type = "password";
      icon.classList.replace("fa-eye-slash", "fa-eye");
    }
  });
});

// Password strength
const pw1 = document.getElementById("id_password1");
const fill = document.getElementById("strengthFill");
const lbl = document.getElementById("strengthLabel");
if (pw1) {
  pw1.addEventListener("input", () => {
    const v = pw1.value;
    let score = 0;
    if (v.length >= 8) score++;
    if (/[A-Z]/.test(v)) score++;
    if (/[0-9]/.test(v)) score++;
    if (/[^A-Za-z0-9]/.test(v)) score++;
    const levels = [
      { pct: "0%", color: "#e5e7eb", text: "" },
      { pct: "25%", color: "#dc2626", text: "Très faible" },
      { pct: "50%", color: "#f59e0b", text: "Moyen" },
      { pct: "75%", color: "#3b82f6", text: "Bon" },
      { pct: "100%", color: "#16a34a", text: "Excellent" },
    ];
    const l = levels[v.length ? score : 0];
    fill.style.width = l.pct;
    fill.style.background = l.color;
    lbl.textContent = l.text;
    lbl.style.color = l.color;
  });
}
