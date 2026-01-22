// static/js/like.js

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}

document.addEventListener("click", async (e) => {
  const btn = e.target.closest(".like-btn");
  if (!btn) return;

  // 비로그인 처리 (서버에서도 login_required로 막히긴 함)
  if (btn.dataset.requiresAuth === "1") {
    alert("로그인 후 좋아요를 누를 수 있어요.");
    return;
  }

  const postId = btn.dataset.postId;
  const url = btn.dataset.likeUrl;
  const csrftoken = getCookie("csrftoken");

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    // login_required가 걸려있으면 보통 302/403 등이 올 수 있음
    if (!res.ok) {
      alert("요청 실패! 로그인 상태를 확인해줘.");
      return;
    }

    const data = await res.json();
    const liked = data.liked;
    const likeCount = data.like_count;

    // 1) 버튼 UI 갱신
    btn.classList.toggle("liked", liked);
    btn.textContent = liked ? "❤️" : "🤍";

    // 2) 카운트 UI 갱신
    const countEl = document.querySelector(`.like-count[data-post-id="${postId}"] b`);
    if (countEl) countEl.textContent = likeCount;

  } catch (err) {
    console.error(err);
    alert("네트워크 오류가 발생했어.");
  }
});
