// プロフィール画像をクリック → ファイル選択 → その場でプレビュー表示

// HTMLの読み込みが終わってから、要素を探す（null事故を防ぐ）
document.addEventListener("DOMContentLoaded", () => {
  // ファイル入力（画像を選ぶinput）
  const input = document.getElementById("profileImageInput");

  // 表示している画像
  const preview = document.getElementById("profilePreview");

  if (!input || !preview) return;

  // inputの値
  input.addEventListener("change", () => {
    if (!input.files || input.files.length === 0) return;
    const file = input.files[0];

    // 画像以外だったら終了
    if (!file.type || !file.type.startsWith("image/")) return;

    const objectUrl = URL.createObjectURL(file);

    preview.src = objectUrl;
  });
});