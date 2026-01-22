# stories/views.py
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import StoryUploadForm
from .models import Story, StoryItem


@login_required
@require_http_methods(["GET", "POST"])
def story_create(request):
    form = StoryUploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        files = request.FILES.getlist("images")
        if not files:
            form.add_error("images", "파일이 서버로 전달되지 않았어요. (multipart/form-data 확인 필요)")
            return render(request, "stories/story_create.html", {"form": form})

        # ✅ 유저당 스토리 1개: 없으면 만들고, 있으면 가져오기
        story, created = Story.objects.get_or_create(author=request.user)

        # ✅ 업로드할 때마다 expires 갱신(기존 스토리도 다시 활성화)
        story.expires_at = timezone.now() + timezone.timedelta(hours=24)
        story.save(update_fields=["expires_at", "updated_at"])

        # ✅ 기존 마지막 order 다음부터 추가
        last_order = StoryItem.objects.filter(story=story).aggregate(m=Max("order"))["m"]
        if last_order is None:
            last_order = -1

        for idx, f in enumerate(files):
            StoryItem.objects.create(
                story=story,
                image=f,
                order=last_order + 1 + idx,
            )

        return redirect("posts:feed")

    return render(request, "stories/story_create.html", {"form": form})


@login_required
def story_view(request, story_id):
    story = get_object_or_404(
        Story.objects.select_related("author").prefetch_related("items"),
        id=story_id,
        expires_at__gt=timezone.now(),
    )
    return render(request, "stories/story_view.html", {"story": story})
