// 責務：
// トースト（messages表示）をクリックで消えるようにする
// #数秒後に自動でも消す

document.addEventListener("DOMContentLoaded", () => {
  // トーストが無いページもあるので安全に
  const toastArea = document.getElementById("toastArea");
  if (!toastArea) return;

  // トーストを消す関数
  const hideToast = () => {
    // display:none にして画面から消す
    toastArea.style.display = "none";
  };

  // どこでもクリックで消す
  document.addEventListener("click", hideToast, { capture: true, once: true });

  // 5秒後に自動で消す
  setTimeout(hideToast, 5000);
});