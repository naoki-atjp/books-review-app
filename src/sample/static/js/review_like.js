
// - localStorage に「このレビューをいいねしたか」を保存 (仮)

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("likeBtn");
  const icon = document.getElementById("likeIcon");
  const countEl = document.getElementById("likeCount");

  // このページにいいねUIが無い場合は何もしない（他ページでエラー防止）
  if (!btn || !icon || !countEl) return;

  // review_id を取得（localStorageのキーに使う）
  const reviewId = btn.dataset.reviewId;

  const storageKey = `revithub_like_${reviewId}`;

  // 1ならいいね済み
  const isLiked = localStorage.getItem(storageKey) === "1";

  // 初期表示を反映
  const render = (liked) => {
    const current = parseInt(countEl.textContent || "0", 10);

    icon.src = liked
      ? icon.src.replace("hart_outline.svg", "hart.svg")
      : icon.src.replace("hart.svg", "hart_outline.svg");

    if (liked) {
      btn.classList.add("bg-[#FFF0F5]");
    } else {
      btn.classList.remove("bg-[#FFF0F5]");
    }
  };

  render(isLiked);

  btn.addEventListener("click", () => {
    const likedNow = localStorage.getItem(storageKey) === "1";
    const nextLiked = !likedNow;

    // localStorage 更新
    localStorage.setItem(storageKey, nextLiked ? "1" : "0");

    // カウント更新（UIだけ）
    const current = parseInt(countEl.textContent || "0", 10);
    const nextCount = nextLiked ? current + 1 : Math.max(current - 1, 0);
    countEl.textContent = String(nextCount);

    render(nextLiked);
  });
});