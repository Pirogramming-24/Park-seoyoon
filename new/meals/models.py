from django.db import models

# Create your models here.
class DinnerRecord(models.Model):
    category = models.CharField(max_length=50)  # 메뉴 종류 (한식, 중식 등)
    menu = models.CharField(max_length=50)  # 추천받은 메뉴 이름

    def __str__(self):
        return f"[{self.category}] {self.menu}"
