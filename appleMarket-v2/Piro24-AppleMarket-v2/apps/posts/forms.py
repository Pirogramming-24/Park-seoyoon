# apps/posts/forms.py
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title", "content", "region", "user", "price",
            "photo", "ingredient_image",
            "calories_kcal", "carbs_g", "protein_g", "fat_g",
        ]
