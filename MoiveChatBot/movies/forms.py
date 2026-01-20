from django import forms
from .models import Movie


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'release_year', 'director', 'genre', 'actors', 
                  'runtime', 'rating', 'review', 'poster']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '영화 제목을 입력하세요'
            }),
            'release_year': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '개봉 년도 (예: 2024)'
            }),
            'director': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '감독 이름을 입력하세요'
            }),
            'genre': forms.Select(attrs={
                'class': 'form-select'
            }),
            'actors': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '주연배우를 입력하세요 (여러 명인 경우 ,로 구분)'
            }),
            'runtime': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '러닝타임 (분 단위)'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'review': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': '영화에 대한 리뷰를 작성해주세요',
                'rows': 5
            }),
            'poster': forms.FileInput(attrs={
                'class': 'form-file',
                'accept': 'image/*'
            }),
        }
