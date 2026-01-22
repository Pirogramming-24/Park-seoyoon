# ai/forms.py
from django import forms


class TextGenerationForm(forms.Form):
    """텍스트 생성 입력 폼"""

    prompt = forms.CharField(
        label="프롬프트",
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "텍스트를 입력하세요...",
                "class": "form-control",
            }
        ),
    )


class ImageGenerationForm(forms.Form):
    """이미지 생성 입력 폼"""

    prompt = forms.CharField(
        label="이미지 프롬프트",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "생성할 이미지를 설명하세요...",
                "class": "form-control",
            }
        ),
    )


class TextRequestForm(forms.Form):
    """
    챌린지 복합 기능 입력 폼
    (입력 1번 → 요약 → 감정분석 → 최종 결과 1개)
    """

    text = forms.CharField(
        label="분석할 텍스트",
        widget=forms.Textarea(
            attrs={
                "rows": 6,
                "placeholder": (
                    "텍스트를 입력하면 요약 후 "
                    "요약된 내용에 대해 감정분석을 수행합니다..."
                ),
                "class": "form-control",
            }
        ),
    )
