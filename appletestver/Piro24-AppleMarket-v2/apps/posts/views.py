# apps/posts/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm
from .tasks import run_ocr_and_analysis
from .utils import extract_ingredients_from_image, analyze_nutrition

from django.shortcuts import render
from .models import Post
import traceback

def main(request):
    posts = Post.objects.all().order_by("-created_at")
    return render(request, "posts/list.html", {"posts": posts})


@csrf_exempt
def api_analyze_image(request):
    """
    이미지 업로드 -> (서버에서) OCR + 분석 -> 결과 JSON
    프론트에서 '분석 중…' 표시 후 응답 오면 자동 채우기
    """
    if request.method != "POST" or not request.FILES.get("image"):
        return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

    image_file = request.FILES["image"]

    path = default_storage.save("tmp/ocr_process.png", image_file)
    full_path = default_storage.path(path)

    try:
        extracted_text = extract_ingredients_from_image(full_path)
        nutrition = analyze_nutrition(extracted_text)

        return JsonResponse({
            "status": "success",
            **nutrition,
            "raw_text": extracted_text,  # 디버깅/개선용(원하면 제거)
        })
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    finally:
        # 임시 파일은 항상 정리
        try:
            default_storage.delete(path)
        except:
            pass
def create(request):
    if request.method == "GET":
        form = PostForm()
        return render(request, "posts/create.html", {"form": form})

    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.analysis_status = "idle"
        post.save()

        if post.ingredient_image:
            post.analysis_status = "processing"
            post.analysis_error = ""
            post.save(update_fields=["analysis_status", "analysis_error"])
            run_ocr_and_analysis.delay(post.id)

        return redirect("posts:detail", pk=post.id)

    return render(request, "posts/create.html", {"form": form})


def detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    return render(request, "posts/detail.html", {"post": post})


def update(request, pk):
    post = get_object_or_404(Post, id=pk)
    old_image = post.ingredient_image.name if post.ingredient_image else None

    if request.method == "GET":
        form = PostForm(instance=post)
        return render(request, "posts/update.html", {"form": form, "post": post})

    form = PostForm(request.POST, request.FILES, instance=post)
    if form.is_valid():
        post = form.save()
        new_image = post.ingredient_image.name if post.ingredient_image else None

        if new_image and new_image != old_image:
            post.analysis_status = "processing"
            post.analysis_error = ""
            post.save(update_fields=["analysis_status", "analysis_error"])
            run_ocr_and_analysis.delay(post.id)

        return redirect("posts:detail", pk=post.id)

    return render(request, "posts/update.html", {"form": form, "post": post})


def delete(request, pk):
    post = get_object_or_404(Post, id=pk)
    post.delete()
    return redirect("posts:main")


def get_analysis_status(request, pk):
    post = get_object_or_404(Post, id=pk)
    return JsonResponse({
        "status": post.analysis_status,  # idle | processing | done | failed
        "error": post.analysis_error,
        "calories_kcal": post.calories_kcal,
        "carbs_g": post.carbs_g,
        "protein_g": post.protein_g,
        "fat_g": post.fat_g,
    })