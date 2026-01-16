# apps/posts/utils.py
import os
import re
import cv2
import numpy as np

_OCR = None
def imread_unicode(path: str):
    """
    Windows에서 한글/유니코드 경로 때문에 cv2.imread가 실패하는 경우를 우회
    """
    data = np.fromfile(path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img

def get_ocr():
    """PaddleOCR는 무겁기 때문에 프로세스당 1회만 생성(싱글턴)"""
    global _OCR
    if _OCR is None:
        from paddleocr import PaddleOCR
        _OCR = PaddleOCR(
            use_angle_cls=False,
            lang="korean",
        )
    return _OCR


def preprocess_for_ocr(image_path: str) -> str:
    """
    OCR 인식률 개선 전처리:
    - grayscale
    - upscale(2x)
    - denoise
    - CLAHE(대비 강화)
    - adaptive threshold
    - morphology close
    """
    img = imread_unicode(image_path)
    if img is None:
        raise ValueError(f"이미지를 읽을 수 없습니다: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    denoised = cv2.GaussianBlur(gray, (3, 3), 0)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(denoised)

    binary = cv2.adaptiveThreshold(
        contrast, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 7
    )

    kernel = np.ones((1, 1), np.uint8)
    morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    out_path = image_path + ".pre.png"
    cv2.imwrite(out_path, morph)
    return out_path


def extract_ingredients_from_image(image_path: str) -> str:
    """
    전처리 후 PaddleOCR로 텍스트 추출
    """
    pre_path = preprocess_for_ocr(image_path)

    ocr = get_ocr()
    result = ocr.ocr(pre_path, cls=True)

    if not result or not result[0]:
        return ""

    texts = []
    for line in result[0]:
        # line: [box, (text, score)]
        text, score = line[1][0], line[1][1]
        # 신뢰도 필터(너무 빡세면 누락될 수 있어 0.4~0.6 사이에서 조정)
        if score >= 0.5:
            texts.append(text)

    return "\n".join(texts)


def _to_float(s: str):
    try:
        # 1,234 같은 경우 대비
        s = s.replace(",", "")
        return float(s)
    except:
        return None


def normalize_text(text: str) -> str:
    t = text.replace(" ", "")
    t = t.replace("㎉", "kcal").replace("ＫＣＡＬ", "kcal").replace("KCAL", "kcal").replace("Kcal", "kcal")
    t = t.replace("ｍｇ", "mg").replace("ＭＧ", "mg").replace("㎎", "mg")
    t = t.replace("ｇ", "g").replace("Ｇ", "g")
    return t


def _extract_value_after_keyword(t: str, keyword: str):
    """
    예: 탄수화물 12g / 탄수화물:12g / 탄수화물12g / 탄수화물 120mg
    """
    # 숫자(정수/소수) + 단위(g|mg) 캡처
    m = re.search(rf"{keyword}[:：]?(?P<num>\d+(?:\.\d+)?)(?P<unit>mg|g)?", t, re.IGNORECASE)
    if not m:
        return None

    num = _to_float(m.group("num"))
    if num is None:
        return None

    unit = (m.group("unit") or "g").lower()
    if unit == "mg":
        num = num / 1000.0  # g으로 통일
    return num


def analyze_nutrition(text: str) -> dict:
    """
    텍스트에서 열량(kcal), 탄수화물/단백질/지방(g) 추출
    단위는 g으로 통일(mg면 g으로 변환)
    """
    t = normalize_text(text)

    # kcal: "열량120kcal", "칼로리 120kcal", "120kcal"
    calories = None
    m = re.search(r"(열량|칼로리)[:：]?(?:총)?(?P<num>\d+(?:\.\d+)?)kcal", t, re.IGNORECASE)
    if m:
        calories = _to_float(m.group("num"))
    else:
        m2 = re.search(r"(?P<num>\d+(?:\.\d+)?)kcal", t, re.IGNORECASE)
        if m2:
            calories = _to_float(m2.group("num"))

    carbs = _extract_value_after_keyword(t, "탄수화물")
    protein = _extract_value_after_keyword(t, "단백질")

    # "포화지방/트랜스지방"이 먼저 잡혀버릴 수 있으니 지방은 약간 방어
    fat = None
    # 지방 키워드가 들어간 모든 후보 중 "포화/트랜스" 제외하고 첫번째
    for m in re.finditer(r"(지방)[:：]?(?P<num>\d+(?:\.\d+)?)(?P<unit>mg|g)?", t, re.IGNORECASE):
        window_start = max(0, m.start() - 4)
        window = t[window_start:m.start()]
        if "포화" in window or "트랜스" in window:
            continue
        num = _to_float(m.group("num"))
        if num is None:
            continue
        unit = (m.group("unit") or "g").lower()
        if unit == "mg":
            num /= 1000.0
        fat = num
        break

    return {
        "calories_kcal": calories,
        "carbs_g": carbs,
        "protein_g": protein,
        "fat_g": fat,
    }
