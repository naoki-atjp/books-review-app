document.addEventListener("DOMContentLoaded", () => {
  const root = document.getElementById("userMenuRoot");
  const button = document.getElementById("userMenuButton");
  const popup = document.getElementById("userMenuPopup");

  if (!root || !button || !popup) return;

  const isOpen = () => !popup.classList.contains("hidden");

  const openMenu = () => {
    popup.classList.remove("hidden");
    button.setAttribute("aria-expanded", "true");
  };

  const closeMenu = () => {
    popup.classList.add("hidden");
    button.setAttribute("aria-expanded", "false");
  };

  // 開閉切り替え
  button.addEventListener("click", (e) => {
    e.stopPropagation();

    if (isOpen()) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  // 外側クリックで閉じる
  document.addEventListener("click", (e) => {
    // rootの外をクリックしたら閉じる
    if (!root.contains(e.target)) closeMenu();
  });

  // Escキーで閉じる
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeMenu();
  });
});