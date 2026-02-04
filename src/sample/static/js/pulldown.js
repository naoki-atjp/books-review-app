// 「並び替え」プルダウン専用の制御
// - ボタンを押すとメニューが開く/閉じる
// - 項目を選ぶと、表示（アイコン/文言）とチェック状態が切り替わる
// - 選択値は hidden input（#sortValue）に保存する（後で並び替え処理に使う）

document.addEventListener("DOMContentLoaded", () => {
  // =========================
  // 1. 使うDOMを取得
  // =========================
  const dropdown = document.getElementById("sortDropdown");
  const button = document.getElementById("sortButton");
  const menu = document.getElementById("sortMenu");

  const iconEl = document.getElementById("sortButtonIcon");
  const textEl = document.getElementById("sortButtonText");

  const sortValueInput = document.getElementById("sortValue");

  // 「このページに並び替えUIが無い」場合は何もしない（他ページでエラー防止）
  if (!dropdown || !button || !menu || !iconEl || !textEl || !sortValueInput) return;

  // メニュー内の各項目ボタンを取得
  const items = menu.querySelectorAll("button[data-value]");

  // =========================
  // 2. 開閉の関数
  // =========================
  const openMenu = () => {
    menu.classList.remove("hidden");
    button.setAttribute("aria-expanded", "true");
  };

  const closeMenu = () => {
    menu.classList.add("hidden");
    button.setAttribute("aria-expanded", "false");
  };

  const toggleMenu = () => {
    const isOpen = button.getAttribute("aria-expanded") === "true";
    if (isOpen) closeMenu();
    else openMenu();
  };

  // =========================
  // 3. 選択状態をUIに反映する関数
  // =========================
  const renderSelected = () => {
    const current = sortValueInput.value;

    items.forEach((item) => {
      // data-* から値を取り出す
      const value = item.dataset.value;
      const label = item.dataset.label;
      const icon = item.dataset.icon;

      // チェックの表示/非表示を切り替える
      const check = item.querySelector(".js-check");
      if (check) {
        if (value === current) check.classList.remove("hidden");
        else check.classList.add("hidden");
      }

      // 選択中のものは、ボタン表示も更新する
      if (value === current) {
        iconEl.src = icon;
        textEl.textContent = label;
      }
    });
  };

  // =========================
  // 4. ボタンクリックで開閉
  // =========================
  button.addEventListener("click", (e) => {
    e.preventDefault();
    toggleMenu();
  });

  // =========================
  // 5. 項目クリックで選択
  // =========================
  items.forEach((item) => {
    item.addEventListener("click", (e) => {
      e.preventDefault();

      // hidden input に選択値を保存
      sortValueInput.value = item.dataset.value;

      // UI反映
      renderSelected();

      // 閉じる
      closeMenu();

      // TODO: ここで並び替えの実処理を入れる（後で）
      // 例：URLに ?sort=likes を付けてリロード、など
    });
  });

  // =========================
  // 6. 外側クリックで閉じる
  // =========================
  document.addEventListener("click", (e) => {
    if (!dropdown.contains(e.target)) {
      closeMenu();
    }
  });

  // 初期表示を整える
  renderSelected();
});