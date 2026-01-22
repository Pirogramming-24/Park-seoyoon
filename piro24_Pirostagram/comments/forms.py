# comments/forms.py
from django import forms
from .models import Comment, Reply


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.TextInput(attrs={"placeholder": "댓글 달기...", "maxlength": 200}),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ["content"]
        widgets = {
            "content": forms.TextInput(attrs={"placeholder": "답글 달기...", "maxlength": 200}),
        }