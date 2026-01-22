from .base import BaseAIService
from transformers import pipeline
from typing import Dict, Any

class ComboService(BaseAIService):
    """
    챌린지 복합 서비스
    처리 흐름:
    입력 텍스트
      → 요약 모델 호출
      → 요약 결과를 감정분석 모델에 전달
      → 하나의 최종 결과로 결합
    """

    SUMMARY_MODEL = "sshleifer/distilbart-cnn-12-6"
    SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    def __init__(self):
        super().__init__()
        self.load_model()

    def load_model(self):
        try:
            self.summarizer = pipeline("summarization", model=self.SUMMARY_MODEL)
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model=self.SENTIMENT_MODEL
            )
        except Exception as e:
            self.summarizer = None
            self.sentiment_analyzer = None
            print("ComboService model load failed:", e)

    def execute(self, input_data: str) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, max_length=2000):
                return {
                    "success": False,
                    "result": None,
                    "error": "입력이 비어있거나 너무 깁니다."
                }

            if not self.summarizer or not self.sentiment_analyzer:
                return {
                    "success": False,
                    "result": None,
                    "error": "모델 로딩 실패"
                }

            # 1️⃣ 요약
            summary_result = self.summarizer(
                input_data,
                max_length=130,
                min_length=30,
                do_sample=False
            )
            summary_text = summary_result[0]["summary_text"]

            # 2️⃣ 감정분석 (요약 결과 기준!)
            sentiment_result = self.sentiment_analyzer(summary_text)
            sentiment_label = sentiment_result[0]["label"]
            sentiment_score = sentiment_result[0]["score"]

            # 3️⃣ 최종 단일 출력 생성
            final_output = (
                "🧩 Combined AI Analysis Result\n\n"
                f"📌 Result:\n{summary_text}\n\n"
                f"{sentiment_label.lower()} "
                f"(confidence: {sentiment_score:.2f})."
            )

            return {
                "success": True,
                "result": final_output,
                "error": None
            }

        except Exception as e:
            return self.format_error(e)
