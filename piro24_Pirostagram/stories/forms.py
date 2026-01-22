# stories/forms.py
from django import forms


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class StoryUploadForm(forms.Form):
    images = forms.FileField(
        widget=MultiFileInput(attrs={"multiple": True, "accept": "image/*"}),
        required=True,
    )
