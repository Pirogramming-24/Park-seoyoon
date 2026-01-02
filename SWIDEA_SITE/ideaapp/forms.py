# ideas/forms.py
from django import forms
from .models import Idea, DevTool

class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ["title", "image", "content", "interest", "devtool"]


class DevToolForm(forms.ModelForm):
    class Meta:
        model = DevTool
        fields = ["name", "kind", "content"]
