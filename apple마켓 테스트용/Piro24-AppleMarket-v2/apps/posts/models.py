from django.db import models
from django.utils import timezone
from apps.users.models import User

# Create your models here.
class Post(models.Model):
    title = models.CharField('제목', max_length=20)
    content = models.CharField('내용', max_length=20)
    region = models.CharField('지역', max_length=20)
    user = models.ForeignKey(User, verbose_name='작성자', on_delete=models.CASCADE)
    price = models.IntegerField('가격', default=1000)
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', null=True, blank=True)
    photo = models.ImageField('이미지', blank=True, upload_to='posts/%Y%m%d') #대표이미지
    ingredient_image = models.ImageField(upload_to="ingredients/", blank=True, null=True) #성분표

    #OCR 원문 
    ingredients_text = models.TextField(blank=True, default="")
    # 분석 결과
    calories_kcal = models.FloatField(blank=True, null=True)
    carbs_g = models.FloatField(blank=True, null=True)
    protein_g = models.FloatField(blank=True, null=True)
    fat_g = models.FloatField(blank=True, null=True)
    # 처리 상태
    analysis_status = models.CharField(
        max_length=20,
        default="idle",  # idle | processing | done | failed
    )
    analysis_error = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs):
        if self.pk:  # 수정일 때에만 갱신
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

#성분표 모델이 없음 현재!
