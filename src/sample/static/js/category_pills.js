document.addEventListener("DOMContentLoaded", () => {

  // =============== カテゴリをクリックしたときの表示 ===============
  document.addEventListener("click", (e) => {
    const pill = e.target.closest(".js-category-pill");
    if (!pill) return;

    pill.classList.toggle("category-active");
    // console.log('クリックしました')

    // プレビューモーダルが開いてるなら、カテゴリバッジを更新
    const previewModal = document.getElementById("previewModal");
    const isOpen = previewModal && !previewModal.classList.contains("hidden");
    if (isOpen && typeof renderCategoryBadges === "function") {
      renderCategoryBadges();
    }
  });


  // =============== 人気書籍カードのカテゴリ幅が親要素を超えた時のスライド動作 ===============
  const categoriesBoxes = document.querySelectorAll(".js-categories");
  if (!categoriesBoxes.length) return;

  const updateOne = (box) => {
    const group = box.querySelector(".js-category-row-group");
    if (!group) return;

    const containerWidth = box.clientWidth;
    const contentWidth = group.scrollWidth;
    const shouldAnimate = contentWidth > containerWidth + 1;
    box.classList.toggle("is-animate", shouldAnimate);
  };

  const updateAll = () => categoriesBoxes.forEach(updateOne);

  // 初回：描画タイミングのズレ対策
  updateAll();
  requestAnimationFrame(updateAll);
  setTimeout(updateAll, 50);

  window.addEventListener("resize", updateAll);

  if ("ResizeObserver" in window) {
    const ro = new ResizeObserver(updateAll);
    categoriesBoxes.forEach((box) => ro.observe(box));
  }

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(updateAll);
  }
});