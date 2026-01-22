# ai/decorators.py
from functools import wraps
from django.http import HttpResponse
from django.urls import reverse


def login_required_with_alert(view_func):
    """
    로그인 필수 데코레이터 (alert 포함)

    동작:
    - 비로그인 사용자가 직접 URL 접근 시
      1) alert("로그인 후 이용해주세요")
      2) 로그인 페이지로 이동 (?next=원래URL)
      3) 로그인 후 원래 페이지로 복귀
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        next_url = request.get_full_path()
        login_url = reverse("account_login")

        html = f"""
        <script>
            alert("로그인 후 이용해주세요");
            window.location.href = "{login_url}?next={next_url}";
        </script>
        """
        return HttpResponse(html)

    return wrapper
