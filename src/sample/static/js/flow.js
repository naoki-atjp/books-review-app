// 学習フロー ON/OFF + STEP追加/削除
// プレビュー表示
document.addEventListener("DOMContentLoaded", () => {

  const toggle = document.getElementById("studyFlowToggle");
  const area = document.getElementById("studyFlowArea");
  const stepsWrap = document.getElementById("studyFlowSteps");
  const addTop = document.getElementById("addStepBtnTop");
  const addBottom = document.getElementById("addStepBtnBottom");
  const enabledHidden = document.getElementById("studyFlowEnabled");

  if (!toggle || !area || !stepsWrap || !addTop || !addBottom || !enabledHidden) return;

  let steps = [];

  // =========================
  // STEPを描画する関数
  // =========================
  const renderSteps = () => {
    stepsWrap.innerHTML = "";

    steps.forEach((step, index) => {
      const stepNo = index + 1;

      // STEPカード
      const card = document.createElement("div");
      card.className = "relative rounded-2xl border border-[#0060e7] bg-[#F2F6FF] flex items-start justify-between gap-4 p-4";

      // 左の番号バッジ
      const badge = document.createElement("div");
      badge.className =
        "w-8 h-8 rounded-full bg-[#2F6FED] text-white flex items-center justify-center text-sm font-semibold";
      badge.textContent = String(stepNo);

      const rightArea = document.createElement("div");
      rightArea.className = "flex-1 min-w-0";

      const header = document.createElement("div");
      header.className = "flex items-start justify-between";

      // タイトル
      const titleInput = document.createElement("input");
      titleInput.type = "text";
      titleInput.name = `step_title_${index}`;
      titleInput.placeholder = "ステップのタイトル";
      titleInput.className =
        "w-full rounded-lg bg-white px-4 py-3 text-sm border border-[#d1d1d1] focus:outline-none focus:ring-1 focus:ring-[#0060e7] mb-4";
      titleInput.value = step.title;
      titleInput.addEventListener("input", (e) => {
        steps[index].title = e.target.value;
      });

      // 削除ボタン
      const removeBtn = document.createElement("button");
      removeBtn.type = "button";
      removeBtn.className =
        "w-8 h-8 rounded-full hover:bg-white/60 text-red-500 flex items-center justify-center";
      removeBtn.textContent = "×";

      // クリックしたらそのSTEPを消して再描画
      removeBtn.addEventListener("click", () => {
        steps.splice(index, 1);
        renderSteps();
      });

      header.appendChild(titleInput);
      header.appendChild(removeBtn);

      // 入力エリア
      const body = document.createElement("div");
      body.className = "mt-4 space-y-3";

      // 詳細
      const descArea = document.createElement("textarea");
      descArea.rows = 3;
      descArea.name = `step_description_${index}`;
      descArea.placeholder = "ステップの詳細説明";
      descArea.className =
        "w-full rounded-lg bg-white px-4 py-3 text-sm border border-[#d1d1d1] focus:outline-none focus:ring-1 focus:ring-[#2F6FED] mb-3";
      descArea.value = step.description;
      descArea.addEventListener("input", (e) => {
        steps[index].description = e.target.value;
      });

      // 所要時間
      const durationInput = document.createElement("input");
      durationInput.type = "text";
      durationInput.name = `step_duration_${index}`;
      durationInput.placeholder = "所要時間（例：1週間）";
      durationInput.className =
        "w-full rounded-lg bg-white px-4 py-3 text-sm border border-[#d1d1d1] focus:outline-none focus:ring-1 focus:ring-[#2F6FED] mr-8";
      durationInput.value = step.duration;
      durationInput.addEventListener("input", (e) => {
        steps[index].duration = e.target.value;
      });

      rightArea.appendChild(header);
      rightArea.appendChild(descArea);
      rightArea.appendChild(durationInput);

      card.appendChild(badge);
      card.appendChild(rightArea);
      card.appendChild(body);

      stepsWrap.appendChild(card);
    });
  };

  // =========================
  // STEP追加
  // =========================
  const addStep = () => {
    steps.push({ title: "", description: "", duration: "" });
    renderSteps();
  };

  addTop.addEventListener("click", addStep);
  addBottom.addEventListener("click", addStep);

  // =========================
  // ON/OFFの挙動
  // =========================
  toggle.addEventListener("change", (e) => {
    const isOn = e.target.checked;

    if (isOn) {
      area.classList.remove("hidden");
      enabledHidden.value = "1";

      // ONにした瞬間にSTEP1を出す
      if (steps.length === 0) {
        steps = [{ title: "", description: "", duration: "" }];
      }
      renderSteps();
    } else {
      area.classList.add("hidden");
      enabledHidden.value = "0";
    }
  });




  const previewOpenBtn = document.getElementById("previewOpenBtn"); // 右下の「プレビュー」ボタン
  const previewModal = document.getElementById("previewModal"); // モーダル全体
  const previewBackdrop = document.getElementById("previewBackdrop"); // 背景
  const previewCloseBtn = document.getElementById("previewCloseBtn"); // ×ボタン

  // プレビュー内の差し込み先
  const previewStars = document.getElementById("previewStars"); // 表示
  const previewRatingText = document.getElementById("previewRatingText"); // 評価数値
  const previewTitle = document.getElementById("previewTitle"); // タイトル
  const previewReviewText = document.getElementById("previewReviewText"); // 本文
  const previewRecommendedFor = document.getElementById("previewRecommendedFor"); // おすすめ
  const previewFlowList = document.getElementById("previewFlowList"); // 学習フロー一覧
  const previewCategoryBadges = document.getElementById("previewCategoryBadges"); // カテゴリ

  // -------------------------
  // HTMLエスケープ
  // -------------------------
  const escapeHtml = (str) => {
    return String(str)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  };

  // -------------------------
  // 星アイコン（SVG）を1つ作る関数
  // type: "full" | "empty"
  // -------------------------
  const createStarSvg = (type) => {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");

    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("width", "18");
    svg.setAttribute("height", "18");
    svg.style.display = "block";
    svg.style.flex = "0 0 auto";
    svg.setAttribute("fill", type === "full" ? "#F4B400" : "#D9D9D9");

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute(
      "d",
      "M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"
    );

    svg.appendChild(path);
    return svg;
  };

  // -------------------------
  // 評価数値から星を描く（0.5刻みでもOK）
  // -------------------------
  const renderStars = (ratingNumber) => {
    if (!previewStars) return;

    previewStars.innerHTML = "";

    const full = Math.floor(ratingNumber);

    for (let i = 0; i < 5; i++) {
      const starType = i < full ? "full" : "empty";
      previewStars.appendChild(createStarSvg(starType));
    }
  };

  // -------------------------
  // カテゴリの選択状態をバッジ表示
  // -------------------------
  const renderCategoryBadges = () => {
    if (!previewCategoryBadges) return;

    previewCategoryBadges.innerHTML = "";

    // category_area.html の範囲だけを見る（他のボタンが混ざらないように）
    const categoryArea = document.getElementById("categoryArea");
    if (!categoryArea) return;

    // 選択中（category-active）になっているものだけ集める
    const activePills = categoryArea.querySelectorAll(
      ".js-category-pill.category-active"
    );

    if (activePills.length === 0) return;

    activePills.forEach((pill) => {
      const name =
        (pill.dataset.categoryName || "").trim() ||
        (pill.textContent || "").trim();

      if (!name) return;

      // バッジを作る
      const span = document.createElement("span");
      span.className =
        "inline-flex items-center px-3 py-1 rounded-full bg-[#DCEBFF] text-[#0B42FF] text-xs";
      span.textContent = name;

      // プレビューの表示欄に追加
      previewCategoryBadges.appendChild(span);
    });
  };

  // -------------------------
  // 学習フロー
  // -------------------------
  const renderFlowCards = () => {
    if (!previewFlowList) return;

    previewFlowList.innerHTML = "";

    // 学習フローOFFなら説明を表示
    if (!toggle.checked) {
      const p = document.createElement("p");
      p.className = "text-sm text-[#707070]";
      p.textContent = "学習フローは追加されていません。";
      previewFlowList.appendChild(p);
      return;
    }

    // ONでも無記入なら説明だけ表示
    if (steps.length === 0) {
      const p = document.createElement("p");
      p.className = "text-sm text-[#707070]";
      p.textContent = "学習フローはまだ入力されていません。";
      previewFlowList.appendChild(p);
      return;
    }

    // steps の内容をカード化
    steps.forEach((step, index) => {
      const card = document.createElement("div");

      card.className =
        "rounded-2xl border border-[#2F6FED] bg-[#F2F6FF] p-6 mb-4";

      // 所要時間
      const durationBadge = step.duration
        ? `
      <span class="
        inline-flex items-center justify-center
        px-3 py-1
        rounded-lg
        border border-[#2F6FED]
        text-[#2F6FED]
        text-xs font-semibold
        bg-white
        truncate
      ">
        ${escapeHtml(step.duration)}
      </span>
    `
        : "";

      // タイトル
      const safeTitle = step.title ? escapeHtml(step.title) : "（タイトル未入力）";

      // 本文
      const safeDesc = step.description ? escapeHtml(step.description) : "";

      // レイアウト
      card.innerHTML = `
    <div class="grid grid-cols-[32px_1fr_100px] gap-x-4 items-start">
      
      <!-- 番号 -->
      <div class="w-8 h-8 rounded-full bg-[#2F6FED] text-white flex items-center justify-center text-sm font-semibold">
        ${index + 1}
      </div>

      <!-- タイトル -->
      <p class="text-base leading-snug">
        ${safeTitle}
      </p>

      <!-- 時間 -->
      <div class="flex justify-end">
        ${durationBadge}
      </div>
    </div>
    <p class="mt-2 pl-8 text-base text-customGray">
      ${safeDesc}
    </p>`;

      previewFlowList.appendChild(card);
    });
  };

  // -------------------------
  // モーダルを開く（フォーム値を読み → UIへ反映 → 表示）
  // -------------------------
  const openPreview = () => {
    if (!previewModal || !previewRatingText || !previewTitle || !previewReviewText || !previewRecommendedFor) return;

    // フォームの値を読む
    const ratingEl = document.querySelector('input[name="rating"]:checked');
    const ratingStr = ratingEl ? ratingEl.value : "";

    const titleEl = document.querySelector('input[name="review_title"]');
    const title = titleEl ? titleEl.value : "";

    const reviewTextEl = document.querySelector('textarea[name="review_text"]');
    const reviewText = reviewTextEl ? reviewTextEl.value : "";

    const recEl = document.querySelector('textarea[name="recommended_for"]');
    const recommendedFor = recEl ? recEl.value : "";

    // モーダルへ反映
    previewRatingText.textContent = ratingStr || "-";

    // 星を描く
    const ratingNumber = ratingStr ? Number(ratingStr) : 0;
    renderStars(ratingNumber);

    previewTitle.textContent = title || "（レビュータイトル未入力）";
    previewReviewText.textContent = reviewText || "（レビュー本文未入力）";
    previewRecommendedFor.textContent = recommendedFor || "（未入力）";

    // カテゴリバッジ表示
    renderCategoryBadges();

    // 学習フローをカード表示
    renderFlowCards();

    // モーダル表示 + 背景スクロール停止
    previewModal.classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
  };

  // -------------------------
  // モーダルを閉じる
  // -------------------------
  const closePreview = () => {
    if (!previewModal) return;

    previewModal.classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
  };

  // -------------------------
  // イベント
  // -------------------------
  if (previewOpenBtn) previewOpenBtn.addEventListener("click", openPreview);
  if (previewBackdrop) previewBackdrop.addEventListener("click", closePreview);
  if (previewCloseBtn) previewCloseBtn.addEventListener("click", closePreview);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closePreview();
  });
});

// TODO: inputに字数制限をつける
// TODO: フローの時間入力の単位を選択式にする
// TODO: 入力可能な情報に制限をかける（セキュリティ対策）
// TODO: 書籍情報をセッションに保存状態で別タブで再登録した場合に、初期タブの書籍情報が更新されてしまう問題の対応