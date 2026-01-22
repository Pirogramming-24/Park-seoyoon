# ai/services/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAIService(ABC):
    """
    모든 AI 서비스의 기반 클래스
    
    설계 의도:
    - 공통 인터페이스 제공 (execute)
    - 입력 검증, 에러 처리 등 공통 로직을 상속받은 클래스에서 재사용
    - 뷰 레이어에서 모델 로직을 완전히 분리
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
    
    @abstractmethod
    def load_model(self):
        """모델 로딩 로직 (각 서비스에서 구현)"""
        pass
    
    @abstractmethod
    def execute(self, input_data: str) -> Dict[str, Any]:
        """
        모델 실행 로직 (각 서비스에서 구현)
        
        Returns:
            Dict: {'success': bool, 'result': Any, 'error': str}
        """
        pass
    
    def validate_input(self, input_data: str, max_length: int = 1000) -> bool:
        """입력 검증 (공통 로직)"""
        if not input_data or not input_data.strip():
            return False
        if len(input_data) > max_length:
            return False
        return True
    
    def format_error(self, error: Exception) -> Dict[str, Any]:
        """에러 포맷팅 (공통 로직)"""
        return {
            'success': False,
            'result': None,
            'error': str(error)
        }