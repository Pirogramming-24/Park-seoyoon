from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'content']
        widgets ={
            "content":forms.Textarea(attrs={"rows":3, "placeholder":"문구 입력..."}),
        }