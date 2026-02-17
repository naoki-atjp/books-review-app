document.addEventListener("DOMContentLoaded", () => {

  // =============== カテゴリをクリックしたときの表示 ===============
  // pillボタン一覧（review_formでもTOPでも存在）
  const pills = document.querySelectorAll(".js-category-pill");

  // 選択状態をためる（重複を防ぐため Set を使う）
  const selected = new Set();

  // 追加：バリデーションで戻ってきた時に、選択状態を復元する
  const hiddenArea = document.getElementById("categoryHiddenFields");
  if (hiddenArea) {
    // hidden の name="categories" を全部拾う
    const hiddenInputs = hiddenArea.querySelectorAll('input[name="categories"]');

    hiddenInputs.forEach((input) => {
      // value（カテゴリ名）を selected に入れる
      selected.add(input.value);
    });

    // selected に入ってるカテゴリを見て、pillの見た目をONにする
    pills.forEach((pill) => {
      const categoryName = pill.dataset.categoryName;
      if (!categoryName) return;

      if (selected.has(categoryName)) {
        pill.classList.add("category-active");
      }
    });
  }


  // pillが1つも無いページではこの機能は不要なので、ここだけスキップ
  if (pills.length) {
    document.addEventListener("click", (e) => {
      // クリックされた要素から、pillボタンを探す
      const pill = e.target.closest(".js-category-pill");
      if (!pill) return;

      // data属性からカテゴリ名を取る（POSTに使う本体）
      const categoryName = pill.dataset.categoryName;
      if (!categoryName) return;

      // すでに選択済みなら削除、未選択なら追加
      if (selected.has(categoryName)) {
        selected.delete(categoryName);
      } else {
        selected.add(categoryName);
      }

      // 見た目をON/OFF（あなたの既存UIそのまま）
      pill.classList.toggle("category-active");

      // プレビューモーダルが開いてるなら、カテゴリバッジを更新
      const previewModal = document.getElementById("previewModal");
      const isOpen = previewModal && !previewModal.classList.contains("hidden");
      if (isOpen && typeof renderCategoryBadges === "function") {
        renderCategoryBadges();
      }
    });
  }

  // -----------------------------
  // submit時に hidden input を作ってPOSTに乗せる（review_formだけ）
  // -----------------------------
  const reviewForm = document.getElementById("reviewForm");

  // reviewForm があるページだけ submit を仕込む（TOPでは存在しない想定）
  if (reviewForm && hiddenArea) {
    reviewForm.addEventListener("submit", () => {
      // 以前作った hidden を全削除（2回送信で増殖しないように）
      hiddenArea.innerHTML = "";

      // Setに入ってるカテゴリ名の分だけ hidden input を作る
      selected.forEach((name) => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "categories"; // Django側：request.POST.getlist("categories")
        input.value = name;
        hiddenArea.appendChild(input);
      });
    });
  }

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