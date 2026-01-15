import cv2 as cv

# 손가락 마디 연결 순서 (직접 정의)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),    # 엄지
    (0, 5), (5, 6), (6, 7), (7, 8),    # 검지
    (9, 10), (10, 11), (11, 12),       # 중지
    (13, 14), (14, 15), (15, 16),      # 약지
    (17, 18), (18, 19), (19, 20),      # 소지
    (5, 9), (9, 13), (13, 17), (0, 17) # 손바닥 안쪽 연결
]


def draw_manual(image, detection_result):
    """OpenCV로 직접 랜드마크 그리기"""
    if detection_result is None or not detection_result.hand_landmarks:
        return image

    h, w, _ = image.shape

    for hand_landmarks in detection_result.hand_landmarks:
        # 1. 좌표 변환 (0~1 실수 -> 픽셀 정수)
        points = []
        for lm in hand_landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            points.append((cx, cy))

        # 2. 마디 연결선 그리기
        for start_idx, end_idx in HAND_CONNECTIONS:
            cv.line(image, points[start_idx], points[end_idx], (0, 255, 0), 2)

        # 3. 랜드마크 점 그리기
        for pt in points:
            cv.circle(image, pt, 5, (0, 0, 255), cv.FILLED)
            
    return image

### "Rock", "Paper", "Scissors" 텍스트를 출력할 수 있는 함수입니다
# 편하게 수정하셔도 되고, 이 함수 말고 따로 작성하신 코드로 사용하셔도 됩니다
def print_RSP_result(image, rps_result):
    # 0 == rock, 1 == paper, 2 == scissors
    if rps_result == None:
        text = ""
    else:
        text_list = ["Rock", "Paper", "Scissors"]
        text = text_list[rps_result]
    
    font = cv.FONT_HERSHEY_SIMPLEX # 표준 폰트
    org = (50, 100)               # 글자가 시작될 좌측 하단 좌표 (x, y)
    font_scale = 2                # 글자 크기
    color = (255, 255, 255)       # 색상 (B, G, R) -> 흰색
    thickness = 3                 # 두께

    cv.putText(image, text, org, font, font_scale, color, thickness)

    return image