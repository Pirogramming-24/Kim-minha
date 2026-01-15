import mediapipe as mp
import math, time
import cv2 as cv
from mediapipe.tasks.python import vision
from mediapipe.tasks import python
from visualization import draw_manual, print_RSP_result


def calculate_distance(landmark1, landmark2):
    """두 랜드마크 사이의 유클리드 거리 계산"""
    return math.sqrt((landmark1.x - landmark2.x)**2 + 
                     (landmark1.y - landmark2.y)**2 + 
                     (landmark1.z - landmark2.z)**2)


def is_finger_extended(hand_landmarks, finger_tip_idx, finger_pip_idx):
    """
    손가락이 펴져있는지 판별
    TIP과 손목(0) 사이의 거리 vs PIP와 손목(0) 사이의 거리 비교
    """
    wrist = hand_landmarks[0]
    tip = hand_landmarks[finger_tip_idx]
    pip = hand_landmarks[finger_pip_idx]
    
    tip_to_wrist = calculate_distance(tip, wrist)
    pip_to_wrist = calculate_distance(pip, wrist)
    
    # TIP이 PIP보다 손목에서 멀면 펴진 것
    return tip_to_wrist > pip_to_wrist


def classify_rps(hand_landmarks):
    """
    가위바위보 판별
    0: Rock(바위), 1: Paper(보), 2: Scissors(가위)
    """
    if not hand_landmarks:
        return None
    
    # 검지, 중지, 약지, 소지가 펴져있는지 확인
    # 엄지는 제외 (판별이 복잡함)
    finger_status = {
        'index': is_finger_extended(hand_landmarks, 8, 6),      # 검지
        'middle': is_finger_extended(hand_landmarks, 12, 10),   # 중지
        'ring': is_finger_extended(hand_landmarks, 16, 14),     # 약지
        'pinky': is_finger_extended(hand_landmarks, 20, 18)     # 소지
    }
    
    # 펴진 손가락 개수 세기
    extended_count = sum(finger_status.values())
    
    # 판별 로직
    if extended_count == 0 or extended_count == 1:
        return 0  # Rock (바위)
    elif extended_count == 4:
        return 1  # Paper (보)
    elif extended_count == 2:
        # 검지와 중지만 펴져있으면 가위
        if finger_status['index'] and finger_status['middle']:
            return 2  # Scissors (가위)
        else:
            return 0  # 애매한 경우 바위로 처리
    else:
        return None  # 판별 불가


# 전역 변수로 detection result 저장
detection_result_global = None
result_lock = False


def result_callback(result, output_image, timestamp_ms):
    """MediaPipe의 비동기 결과 처리 콜백"""
    global detection_result_global, result_lock
    if not result_lock:
        detection_result_global = result


def main():
    global detection_result_global, result_lock
    
    # Hand Landmarker 옵션 설정
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        result_callback=result_callback
    )
    
    # Hand Landmarker 생성
    landmarker = vision.HandLandmarker.create_from_options(options)
    
    # 웹캠 열기
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return
    
    print("Press 'q' to quit")
    
    frame_timestamp = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame. Exiting...")
                break
            
            # 좌우 반전 (거울 모드)
            frame = cv.flip(frame, 1)
            
            # BGR을 RGB로 변환
            rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            
            # MediaPipe Image 객체 생성
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # 비동기로 hand landmark 검출
            frame_timestamp += 1
            landmarker.detect_async(mp_image, frame_timestamp)
            
            # 검출 결과가 있으면 처리
            if detection_result_global is not None:
                result_lock = True
                
                # 랜드마크 그리기
                frame = draw_manual(frame, detection_result_global)
                
                # 가위바위보 판별
                rps_result = None
                if detection_result_global.hand_landmarks:
                    hand_landmarks = detection_result_global.hand_landmarks[0]
                    rps_result = classify_rps(hand_landmarks)
                
                # 결과 텍스트 출력
                frame = print_RSP_result(frame, rps_result)
                
                result_lock = False
            
            # 화면에 표시
            cv.imshow('Rock-Paper-Scissors Game', frame)
            
            # 'q' 키를 누르면 종료
            if cv.waitKey(1) == ord('q'):
                break
            
            # 프레임 간 딜레이 (CPU 부하 감소)
            time.sleep(0.01)
    
    finally:
        cap.release()
        cv.destroyAllWindows()
        landmarker.close()


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    # 실행 로직
    None