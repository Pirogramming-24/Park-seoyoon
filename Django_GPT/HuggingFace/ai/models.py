# ai/models.py
from django.db import models
from django.contrib.auth.models import User

class ChatLog(models.Model):
    """
    AI 대화 히스토리 저장
    - user: 로그인한 사용자 (ForeignKey)
    - task: 어떤 탭/기능인지 구분 (text_generation, image_generation, hybrid)
    - user_input: 사용자 입력 텍스트
    - model_output: AI 모델 출력 결과 (JSON 직렬화 가능)
    - created_at: 생성 시각
    
    설계 의도: task로 탭을 구분하여, 각 탭별 히스토리를 쉽게 필터링
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_logs')
    task = models.CharField(max_length=50)  # text_generation, image_generation, hybrid
    user_input = models.TextField()
    model_output = models.TextField()  # JSON string으로 저장
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']  # 최신순 정렬
        indexes = [
            models.Index(fields=['user', 'task', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.task} - {self.created_at}"