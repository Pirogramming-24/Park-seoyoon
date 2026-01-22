# ai/services/image.py
from .base import BaseAIService
from typing import Dict, Any
import requests
from django.conf import settings
import io
from PIL import Image
import uuid
import os

class ImageGenerationService(BaseAIService):
    """
    이미지 생성 서비스 (Hugging Face Inference API 사용)
    모델: stabilityai/stable-diffusion-xl-base-1.0 (SDXL)

    설계 의도:
    - 로컬 GPU 불필요 (HF API 활용)
    - HF_TOKEN으로 API 인증
    - 생성 이미지를 media/images에 저장하고 URL 반환
    """

    API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"


    def __init__(self):
        super().__init__()
        self.load_model()

    def load_model(self):
        """API 방식이므로 모델 로딩은 없고 헤더만 준비"""
        token = getattr(settings, "HF_TOKEN", None)
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def execute(self, input_data: str) -> Dict[str, Any]:
        """
        이미지 생성 실행

        Returns:
            {'success': True, 'result': '/media/images/xxx.png', 'error': None}
        """
        try:
            if not self.validate_input(input_data, max_length=500):
                return {
                    "success": False,
                    "result": None,
                    "error": "프롬프트가 비어있거나 너무 깁니다."
                }

            if not getattr(settings, "HF_TOKEN", None):
                return {
                    "success": False,
                    "result": None,
                    "error": "HF_TOKEN이 설정되지 않았습니다. (.env → settings.py 로드 확인)"
                }

            # HF Inference API 호출
            response = requests.post(
                self.API_URL,
                headers=self.headers,
                json={"inputs": input_data},
                timeout=90
            )

            if response.status_code != 200:
                # 모델 로딩 중일 때 503이 자주 떠서 메시지에 response.text 포함
                return {
                    "success": False,
                    "result": None,
                    "error": f"API 오류: {response.status_code} - {response.text}"
                }

            # 이미지 바이너리 → PIL Image
            image_bytes = response.content
            image = Image.open(io.BytesIO(image_bytes))

            # 저장 경로
            filename = f"{uuid.uuid4().hex}.png"
            save_dir = os.path.join(settings.MEDIA_ROOT, "images")
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, filename)

            image.save(save_path)

            image_url = f"{settings.MEDIA_URL}images/{filename}"

            return {
                "success": True,
                "result": image_url,
                "error": None
            }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "result": None,
                "error": "API 요청 시간 초과. 다시 시도해주세요."
            }
        except Exception as e:
            return self.format_error(e)
