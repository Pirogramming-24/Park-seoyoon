from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .upstage_utils import retrieve_top_k_movies, upstage_chat


def chatbot_page(request):
    return render(request, "chatbot/chatbot.html")


@require_POST
def chatbot_response(request):
    message = (request.POST.get("message") or "").strip()
    if not message:
        return JsonResponse({"answer": "메시지를 입력해줘."})

    top = retrieve_top_k_movies(message, k=5)

    context_lines = []
    for m, score in top:
        context_lines.append(
            f"- {m.title} ({m.release_year}, {m.genre}, 별점 {m.rating})\n"
            f"  감독: {m.director or '-'}\n"
            f"  배우: {m.actors or '-'}\n"
            f"  리뷰: {m.review or '-'}"
        )

    system = (
        "너는 영화 사이트의 챗봇이다. "
        "아래 [검색 결과]를 근거로만 답해라. "
        "근거가 부족하면 부족하다고 말하고, 가능하면 추가 질문을 해라."
    )

    user = f"""[검색 결과]
{chr(10).join(context_lines)}

[사용자 질문]
{message}
"""

    answer = upstage_chat(system=system, user=user)
    return JsonResponse({"answer": answer})
