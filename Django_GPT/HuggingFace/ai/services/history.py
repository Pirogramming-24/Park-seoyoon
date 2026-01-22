# ai/services/history.py
from typing import List, Dict, Any, Optional
from ai.models import ChatLog
from django.contrib.auth.models import User
import json

class HistoryManager:
    """
    히스토리 저장/로드 관리 클래스
    
    설계 의도:
    - 로그인/비로그인 상태에 따라 다른 처리
    - 로그인: DB 저장
    - 비로그인: 세션에 저장 (POST 직후에만 표시, GET시 초기화)
    - 뷰에서 분기 로직 제거, 히스토리 관련 로직을 한 곳에 집중
    """
    
    @staticmethod
    def save_history(
        user: Optional[User],
        task: str,
        user_input: str,
        model_output: Any,
        request=None
    ) -> None:
        """
        히스토리 저장
        
        Args:
            user: 로그인한 유저 (None이면 비로그인)
            task: 작업 유형 (text_generation, image_generation, hybrid)
            user_input: 사용자 입력
            model_output: 모델 출력 (dict 또는 str)
            request: Django request 객체 (비로그인 세션용)
        """
        output_str = json.dumps(model_output) if isinstance(model_output, dict) else str(model_output)
        
        if user and user.is_authenticated:
            # 로그인: DB 저장
            ChatLog.objects.create(
                user=user,
                task=task,
                user_input=user_input,
                model_output=output_str
            )
        elif request:
            # 비로그인: 세션에 임시 저장 (POST 직후 표시용)
            # 주의: GET 요청 시 초기화되므로, 새로고침하면 사라짐
            session_key = f'temp_history_{task}'
            request.session[session_key] = {
                'user_input': user_input,
                'model_output': output_str
            }
    
    @staticmethod
    def load_history(
        user: Optional[User],
        task: str,
        request=None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        히스토리 로드
        
        Args:
            user: 로그인한 유저 (None이면 비로그인)
            task: 작업 유형
            request: Django request 객체 (비로그인 세션용)
            limit: 최대 개수
        
        Returns:
            [{'user_input': ..., 'model_output': ..., 'created_at': ...}, ...]
        """
        if user and user.is_authenticated:
            # 로그인: DB에서 로드
            logs = ChatLog.objects.filter(user=user, task=task)[:limit]
            return [
                {
                    'user_input': log.user_input,
                    'model_output': log.model_output,
                    'created_at': log.created_at
                }
                for log in logs
            ]
        elif request and request.method == 'POST':
            # 비로그인 + POST 직후: 세션에서 로드 (1개만)
            session_key = f'temp_history_{task}'
            temp_history = request.session.get(session_key)
            if temp_history:
                return [temp_history]
        
        # 비로그인 + GET: 빈 리스트 (새로고침 시 초기화)
        return []
    
    @staticmethod
    def clear_session_history(request, task: str) -> None:
        """
        세션 히스토리 삭제 (비로그인용)
        GET 요청 시 명시적으로 호출하여 초기화
        """
        session_key = f'temp_history_{task}'
        if session_key in request.session:
            del request.session[session_key]