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

// QR Scanner
const statusEl = document.getElementById("scanStatus");

function onScanSuccess(decodedText) {
  statusEl.className = "scan-status success";
  statusEl.innerHTML =
    '<i class="fa fa-circle-check"></i> QR code détecté — redirection…';
  setTimeout(() => {
    window.location.href = decodedText;
  }, 600);
}

function onScanError(error) {
  // Silencieux — erreurs fréquentes pendant le scan
}

const scanner = new Html5QrcodeScanner(
  "reader",
  { fps: 10, qrbox: { width: 250, height: 250 }, rememberLastUsedCamera: true },
  false,
);
scanner.render(onScanSuccess, onScanError);
