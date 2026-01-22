# ai/views.py
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .forms import TextGenerationForm, ImageGenerationForm, TextRequestForm
from .services.text import TextGenerationService
from .services.image import ImageGenerationService
from .services.combo import ComboService
from .services.history import HistoryManager
from .decorators import login_required_with_alert

"""
뷰 설계 원칙:
- 뷰는 최대한 얇게: Form 처리 → Service 실행 → 히스토리 저장 → 렌더링
- 비즈니스 로직은 모두 Service 레이어로 분리
- 히스토리 관리는 HistoryManager에 위임
- 로그인 제한은 데코레이터로 처리
"""

# ==================== 공개 탭 (비로그인 허용) ====================

def home(request):
    return render(request, "ai/generate_text.html")





@require_http_methods(["GET", "POST"])
def generate_text_view(request):
    """
    텍스트 생성 탭 (공개)
    - 비로그인 사용자도 접근 가능
    - GET 시: 비로그인 히스토리 초기화
    - POST 시: 결과를 세션에 임시 저장 후 표시
    """
    form = TextGenerationForm()
    result = None
    error = None
    history = []
    
    # GET 요청: 비로그인 세션 히스토리 초기화 (새로고침 시 초기화)
    if request.method == 'GET':
        if not request.user.is_authenticated:
            HistoryManager.clear_session_history(request, 'text_generation')
    
    # POST 요청: 모델 실행
    if request.method == 'POST':
        form = TextGenerationForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['prompt']
            
            # 서비스 실행
            service = TextGenerationService()
            output = service.execute(prompt)
            
            if output['success']:
                result = output['result']
                # 히스토리 저장
                HistoryManager.save_history(
                    user=request.user if request.user.is_authenticated else None,
                    task='text_generation',
                    user_input=prompt,
                    model_output=result,
                    request=request
                )
            else:
                error = output['error']
    
    # 히스토리 로드
    history = HistoryManager.load_history(
        user=request.user if request.user.is_authenticated else None,
        task='text_generation',
        request=request
    )
    
    return render(request, 'ai/generate_text.html', {
        'form': form,
        'result': result,
        'error': error,
        'history': history
    })


# ==================== 제한 탭 (로그인 필요) ====================

@login_required_with_alert
@require_http_methods(["GET", "POST"])
def generate_image_view(request):
    """
    이미지 생성 탭 (로그인 필요)
    - 로그인한 사용자만 접근 가능
    - DB에 히스토리 저장
    """
    form = ImageGenerationForm()
    result = None
    error = None
    history = []
    
    if request.method == 'POST':
        form = ImageGenerationForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['prompt']
            
            # 서비스 실행
            service = ImageGenerationService()
            output = service.execute(prompt)
            
            if output['success']:
                result = output['result']  # 이미지 URL
                # 히스토리 저장
                HistoryManager.save_history(
                    user=request.user,
                    task='image_generation',
                    user_input=prompt,
                    model_output=result,
                    request=request
                )
            else:
                error = output['error']
    
    # 히스토리 로드 (최근 20개)
    history = HistoryManager.load_history(
        user=request.user,
        task='image_generation',
        limit=20
    )
    
    return render(request, 'ai/generate_image.html', {
        'form': form,
        'result': result,
        'error': error,
        'history': history
    })


@login_required_with_alert
@require_http_methods(["GET", "POST"])
def combo_view(request):
    service = ComboService()
    result = None

    form = TextRequestForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        input_text = form.cleaned_data["text"]
        response = service.execute(input_text)

        if response["success"]:
            result = response["result"]
        else:
            result = response["error"]

    return render(
        request,
        "ai/combo.html",
        {
            "form": form,
            "result": result
        }
    )
