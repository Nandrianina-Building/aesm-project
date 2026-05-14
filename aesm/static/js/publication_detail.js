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

// CSRF
function getCookie(name) {
  return document.cookie
    .split("; ")
    .find((r) => r.startsWith(name + "="))
    ?.split("=")[1];
}
const csrftoken = getCookie("csrftoken");

// Like
document.querySelectorAll(".like-btn").forEach((button) => {
  button.addEventListener("click", function () {
    const pubId = this.dataset.id;
    const url = this.dataset.url;
    const icon = this.querySelector("i");
    const text = this.querySelector(".like-text");

    fetch(url, { method: "POST", headers: { "X-CSRFToken": csrftoken } })
      .then((r) => r.json())
      .then((data) => {
        document.getElementById(`count-${pubId}`).textContent = data.like_count;
        if (data.liked) {
          icon.classList.replace("fa-regular", "fa-solid");
          icon.classList.add("liked");
          text.textContent = "J'aime déjà";
          button.classList.add("is-liked");
        } else {
          icon.classList.replace("fa-solid", "fa-regular");
          icon.classList.remove("liked");
          text.textContent = "J'aime";
          button.classList.remove("is-liked");
        }
      });
  });
});
