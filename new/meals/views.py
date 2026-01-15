from django.shortcuts import render
import random
from .models import DinnerRecord #모델을 쓰기 위해 추가

def meals_index(request):
    # 메뉴 목록
    menus = {
        "korean": ["비빔밥", "김치찌개", "불고기", "제육볶음"],
        "chinese": ["짜장면", "짬뽕", "탕수육", "마라탕"],
        "japanese": ["초밥", "돈카츠", "라멘", "우동"],
        "western": ["파스타", "피자", "스테이크", "햄버거"]
    }

    category = request.GET.get('category')  # 선택한 음식 종류
    result = None  # 추천 결과 저장용 변수

    # 추천 로직
    if category in menus:
        result = random.choice(menus[category])
        DinnerRecord.objects.create(category=category, menu=result)  # (추가) DB에 저장
    elif category == "any":
        all_items = sum(menus.values(), [])
        result = random.choice(all_items)
        DinnerRecord.objects.create(category="아무거나", menu=result) # (추가) DB에 저장

    # (추가) 최근 추천 2개만 보기
    records = DinnerRecord.objects.all().order_by('-id')[:2]

    return render(request, 'meals_index.html', {
        'result': result,
        'records': records, #(추가)
        'category': category
    })
