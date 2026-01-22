function safeParseJsonArray(str) {
  try {
    const arr = JSON.parse(str);
    return Array.isArray(arr) ? arr : [];
  } catch (e) {
    console.log("[story] JSON parse error:", e, str);
    return [];
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector(".story-page");
  if (!root) return;

  const urls = safeParseJsonArray(root.dataset.storyUrls);
  const redirectUrl = (root.dataset.redirectUrl || "/").trim();
  const intervalMs = 3000;

  console.log("[story] urls.length =", urls.length);

  const imgEl = document.getElementById("storyImage");
  const progressEl = document.getElementById("storyProgress");

  if (!imgEl || urls.length === 0) {
    window.location.href = redirectUrl;
    return;
  }

  let idx = 0;
  let timeoutId = null;

  const segFills = [];

  function buildProgress(total) {
    if (!progressEl) return;
    progressEl.innerHTML = "";
    segFills.length = 0;

    for (let i = 0; i < total; i++) {
      const seg = document.createElement("div");
      seg.className = "story-seg";

      const fill = document.createElement("div");
      fill.className = "story-seg-fill";

      seg.appendChild(fill);
      progressEl.appendChild(seg);
      segFills.push(fill);
    }
  }

  function animateCurrentFill(i) {
    const fill = segFills[i];
    if (!fill) return;

    // 과거 100 / 미래 0
    for (let k = 0; k < segFills.length; k++) {
      const f = segFills[k];
      f.style.transition = "none";
      if (k < i) f.style.width = "100%";
      if (k > i) f.style.width = "0%";
    }

    // 현재 0 -> 100
    fill.style.transition = "none";
    fill.style.width = "0%";

    requestAnimationFrame(() => {
      fill.style.transition = `width ${intervalMs}ms linear`;
      fill.style.width = "100%";
    });
  }

  function show(i) {
    idx = i;
    imgEl.src = urls[idx];
    animateCurrentFill(idx);
  }

  function stopTimer() {
    if (timeoutId) clearTimeout(timeoutId);
    timeoutId = null;
  }

  function scheduleNext() {
    stopTimer();
    timeoutId = setTimeout(() => {
      goNext();
    }, intervalMs);
  }

  function goNext() {
    // 마지막이면 종료
    if (idx + 1 >= urls.length) {
      window.location.href = redirectUrl;
      return;
    }

    show(idx + 1);
    scheduleNext(); // 다음 예약
  }

  // 초기
  buildProgress(urls.length);
  show(0);
  scheduleNext();

  // 클릭하면 다음
  root.addEventListener("click", (e) => {
    const a = e.target.closest("a");
    if (a) return; // 닫기 링크 제외
    goNext();
  });

  // 탭 비활성화/활성화 시 타이머 제어 (선택)
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stopTimer();
    else scheduleNext();
  });
});
