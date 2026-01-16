# apps/posts/tasks.py
from celery import shared_task
from django.db import transaction
from .models import Post
from .utils import extract_ingredients_from_image, analyze_nutrition

@shared_task
def run_ocr_and_analysis(post_id: int):
    post = Post.objects.get(id=post_id)

    if not post.ingredient_image:
        post.analysis_status = "failed"
        post.analysis_error = "성분표 이미지가 없습니다."
        post.save(update_fields=["analysis_status", "analysis_error"])
        return

    try:
        text = extract_ingredients_from_image(post.ingredient_image.path)
        nutrition = analyze_nutrition(text)

        with transaction.atomic():
            post.ingredients_text = text
            post.calories_kcal = nutrition["calories_kcal"]
            post.carbs_g = nutrition["carbs_g"]
            post.protein_g = nutrition["protein_g"]
            post.fat_g = nutrition["fat_g"]
            post.analysis_status = "done"
            post.analysis_error = ""
            post.save(update_fields=[
                "ingredients_text",
                "calories_kcal", "carbs_g", "protein_g", "fat_g",
                "analysis_status", "analysis_error",
            ])
    except Exception as e:
        post.analysis_status = "failed"
        post.analysis_error = str(e)
        post.save(update_fields=["analysis_status", "analysis_error"])
