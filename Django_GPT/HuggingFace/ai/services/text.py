# ai/services/text.py
from .base import BaseAIService
from transformers import pipeline
from typing import Dict, Any

class TextGenerationService(BaseAIService):
    """
    텍스트 생성 서비스 (로컬 추론 / 공개 모델)
    모델: EleutherAI/gpt-neo-125M

    설계 의도:
    - gated 모델 금지(과제 조건) → 공개 모델 사용
    - pipeline 기반으로 간단/안정적으로 로딩
    - HF_TOKEN 없이도 동작 (로컬 다운로드+캐시 후 실행)
    """

    MODEL_NAME = "EleutherAI/gpt-neo-125M"

    def __init__(self):
        super().__init__()
        self.load_model()

    def load_model(self):
        """텍스트 생성 모델 로딩"""
        try:
            self.generator = pipeline(
                "text-generation",
                model=self.MODEL_NAME
            )
            print("✓ Text generation model loaded:", self.MODEL_NAME)
        except Exception as e:
            print(f"✗ Text generation model loading failed: {e}")
            self.generator = None

    def execute(self, input_data: str) -> Dict[str, Any]:
        """
        텍스트 생성 실행

        Returns:
            {'success': True, 'result': '생성된 텍스트', 'error': None}
        """
        try:
            if not self.validate_input(input_data, max_length=2000):
                return {
                    "success": False,
                    "result": None,
                    "error": "입력이 비어있거나 너무 깁니다."
                }

            if self.generator is None:
                return {
                    "success": False,
                    "result": None,
                    "error": "모델 로딩에 실패했습니다."
                }

            outputs = self.generator(
                input_data,
                max_new_tokens=120,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
            )

            generated_text = outputs[0]["generated_text"]

            return {
                "success": True,
                "result": generated_text,
                "error": None
            }

        except Exception as e:
            return self.format_error(e)
