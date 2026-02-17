// いいねボタンを押したらサーバーへPOST
// 返ってきた likes_count / liked で表示更新

document.addEventListener("DOMContentLoaded", () => {
  const likeBtn = document.getElementById("likeBtn");
  const likeCountEl = document.getElementById("likeCount");
  const likeIcon = document.getElementById("likeIcon");

  if (!likeBtn || !likeCountEl || !likeIcon) return;

  // data属性から必要情報を読む
  const likeUrl = likeBtn.dataset.likeUrl; // テンプレで生成したURLを使う

  if (!likeUrl) return;

  // CSRFトークン取得
  const getCsrfToken = () => {
    // cookie から csrftoken を取る
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  };

  // UI反映用関数
  const applyLikedUi = (liked) => {
    likeIcon.src = liked
      ? "/static/img/hart.svg"
      : "/static/img/hart_outline.svg";
  };

  // クリックでPOSTしてトグル
  likeBtn.addEventListener("click", async () => {
    try {
      // 二重クリック防止
      likeBtn.disabled = true;

      const res = await fetch(likeUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({}), // 今は空
      });

      if (!res.ok) {
        console.error("like toggle failed:", res.status);
        return;
      }

      const data = await res.json();

      if (!data.ok) return;

      // 最新の状態でUI更新
      if (typeof data.likes_count !== "undefined") {
        likeCountEl.textContent = String(data.likes_count);
      }
      applyLikedUi(!!data.liked);
    } catch (e) {
      console.error(e);
    } finally {
      likeBtn.disabled = false;
    }
  });
});