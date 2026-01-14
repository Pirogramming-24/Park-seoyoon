import mediapipe as mp
import math, time
import cv2 as cv
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from visualization import draw_manual, print_RSP_result

# MediaPipe Hand Landmarker 초기화
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
detector = vision.HandLandmarker.create_from_options(options)


def count_extended_fingers(hand_landmarks):
    """펴진 손가락 개수를 세는 함수
    
    Args:
        hand_landmarks: list of landmark objects
    
    Returns:
        int: 펴진 손가락 개수 (0~5)
    """
    # 손가락 끝과 중간 마디 인덱스
    finger_tips = [4, 8, 12, 16, 20]
    finger_pips = [3, 6, 10, 14, 18]
    
    extended_count = 0
    
    # 엄지 판단 (x좌표 차이)
    thumb_tip = hand_landmarks[finger_tips[0]]
    thumb_pip = hand_landmarks[finger_pips[0]]
    if abs(thumb_tip.x - thumb_pip.x) > 0.04:
        extended_count += 1
    
    # 나머지 손가락 판단 (y좌표 비교)
    for i in range(1, 5):
        tip = hand_landmarks[finger_tips[i]]
        pip = hand_landmarks[finger_pips[i]]
        if tip.y < pip.y:
            extended_count += 1
    
    return extended_count


def classify_rps(hand_landmarks):
    """가위바위보 분류 함수
    
    Args:
        hand_landmarks: list of landmark objects
    
    Returns:
        int or None: 0(Rock), 1(Paper), 2(Scissors), None(판정 불가)
    """
    if not hand_landmarks:
        return None
    
    extended = count_extended_fingers(hand_landmarks)
    
    if extended <= 1:
        return 0  # Rock
    elif extended >= 4:
        return 1  # Paper
    elif 2 <= extended <= 3:
        return 2  # Scissors
    else:
        return None


if __name__ == "__main__":
    # 웹캠 초기화
    cap = cv.VideoCapture(0)
    
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    
    print("=== 가위바위보 인식 시작 ===")
    print("카메라에 손을 보여주세요!")
    print("종료: 'q' 키를 누르세요")
    print("=" * 30)
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Can't receive frame. Exiting...")
            break
        
        # 좌우 반전
        frame = cv.flip(frame, 1)
        
        # BGR을 RGB로 변환
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        
        # MediaPipe Image 객체 생성
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # 손 인식 수행
        detection_result = detector.detect(mp_image)
        
        # 가위바위보 판정
        rps_result = None
        if detection_result.hand_landmarks:
            hand_landmarks = detection_result.hand_landmarks[0]
            rps_result = classify_rps(hand_landmarks)
            
            # 손 랜드마크 그리기
            frame = draw_manual(frame, detection_result)
        
        # 가위바위보 결과 텍스트 표시
        frame = print_RSP_result(frame, rps_result)
        
        # 화면 표시
        cv.imshow('Rock Paper Scissors Game', frame)
        
        # 'q' 키로 종료
        if cv.waitKey(1) == ord('q'):
            break
    
    # 리소스 정리
    cap.release()
    cv.destroyAllWindows()
    
    print("프로그램 종료")