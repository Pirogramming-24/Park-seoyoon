from .models import Idea, DevTool

def sidebar_lists(request):
    return {
        "sidebar_ideas": Idea.objects.order_by("-created_at")[:20],  # 최근 20개
        "sidebar_devtools": DevTool.objects.order_by("name")[:50],   # 이름순 50개
    }
