# ai/services/hybrid.py
from .base import BaseAIService
from transformers import pipeline
from typing import Dict, Any

class HybridService(BaseAIService):
    """
    혼합 서비스: 요약 + 감정분석 파이프라인

    모델(공개/접근 제한 없음):
    - 요약: sshleifer/distilbart-cnn-12-6
    - 감정분석: cardiffnlp/twitter-roberta-base-sentiment-latest

    설계 의도:
    - 2개 이상의 모델을 순차 실행(요약 → 감정)
    - 하나의 서비스 클래스에서 결과를 dict로 묶어 반환
    """

    SUMMARIZE_MODEL = "sshleifer/distilbart-cnn-12-6"
    SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    def __init__(self):
        super().__init__()
        self.load_model()

    def load_model(self):
        """요약 및 감정분석 모델 로딩"""
        try:
            self.summarizer = pipeline("summarization", model=self.SUMMARIZE_MODEL)
            self.sentiment_analyzer = pipeline("sentiment-analysis", model=self.SENTIMENT_MODEL)
            print("✓ Hybrid models loaded:", self.SUMMARIZE_MODEL, "/", self.SENTIMENT_MODEL)
        except Exception as e:
            print(f"✗ Hybrid model loading failed: {e}")
            self.summarizer = None
            self.sentiment_analyzer = None

    def execute(self, input_data: str) -> Dict[str, Any]:
        """
        혼합 기능 실행 (요약 → 감정분석)

        Returns:
            {
              'success': True,
              'result': {'summary': ..., 'sentiment': ..., 'confidence': ...},
              'error': None
            }
        """
        try:
            if not self.validate_input(input_data, max_length=2000):
                return {
                    "success": False,
                    "result": None,
                    "error": "텍스트가 비어있거나 너무 깁니다."
                }

            if self.summarizer is None or self.sentiment_analyzer is None:
                return {
                    "success": False,
                    "result": None,
                    "error": "모델 로딩에 실패했습니다."
                }

            # 1) 요약
            summary_output = self.summarizer(
                input_data,
                max_length=130,
                min_length=30,
                do_sample=False
            )
            summary_text = summary_output[0]["summary_text"]

            # 2) 감정분석 (너무 긴 텍스트는 잘라서)
            sentiment_output = self.sentiment_analyzer(input_data[:512])
            sentiment_label = sentiment_output[0]["label"]
            sentiment_score = float(sentiment_output[0]["score"])

            return {
                "success": True,
                "result": {
                    "summary": summary_text,
                    "sentiment": sentiment_label,
                    "confidence": round(sentiment_score, 4)
                },
                "error": None
            }

        except Exception as e:
            return self.format_error(e)
