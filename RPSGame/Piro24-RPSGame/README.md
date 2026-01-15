# ✊✋✌️ Piro24-RPSGame

피로그래밍 24기 4주차 컴퓨터 비전 세션 과제를 위한 스켈레톤 코드입니다.

피로그래밍 24기 4주차 화요일 과제: MediaPipe 기반 실시간 손동작 인식 및 분류 알고리즘 구현

## 📚 과제 목표
- 컴퓨터 비전을 활용한 실시간 인식 기술 실습

## 과제 및 스켈레톤 코드 설명
MediaPipe의 Hand Landmarker는 사람 손에서 총 21개의 랜드마크를 감지합니다

![랜드마크 이미지](./README_image/hand-landmarks.png)

감지할 수 있는 랜드마크를 기반으로 가위, 바위, 보를 인식하는 로직을 구현해주세요

### [참고] 공식 사이트
- [MediaPipe: Hand Landmarker 모델 설명 공식 문서](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker?hl=ko)
- [공식 문서에서 제공하는 파이썬 활용 가이드](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python?hl=ko)
    - `실시간 스트림`을 기준으로 참고해서 코드를 작성하시면 됩니다

- [코드 예시 - Colab](https://colab.research.google.com/github/googlesamples/mediapipe/blob/main/examples/hand_landmarker/python/hand_landmarker.ipynb?hl=ko)

### [참고22] 초기 세팅 가이드
공식 문서와 Colab 기반의 초기 세팅 가이드
과제 시작이 막막할 때 참고해주세요:

1. 시작 부분은 기존과 동일합니다 - 본인 디렉토리 생성
   
2. 프로젝트 클론 받기(bash)
```
git clone https://github.com/j2nii/Piro24-RPSGame.git
```

3. 가상환경 세팅은 기존과 동일하게 해주시면 됩니다(bash)
```
python -m venv venv
```

4. mediapipe 패키지 설치(bash)
```
pip install mediapipe
```
필요하다면 opencv-python 패키지도 설치해주세요

5. hand_landmarker 모델 다운로드(bash)
```
curl -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

6. 이제 스켈레톤 코드를 활용하시면 됩니다!
    - `visualization.py`
        - `draw_manual` 함수: landmarks 시각화 함수
            공식 코랩 코드에서는 `mediapipe.solutions`로 시각화를 진행
            오류가 나는 경우 사용 가능한 cv2를 활용한 landmarks 시각화 함수
        - (참고)`print_RSP_result` 함수: 가위, 바위, 보 출력 함수 - 당연히 이 함수 말고 따로 코딩하셔도 됩니다 :)

    - `webcam.py`: openCV 기반 카메라 비디오 라이브 스트림 레거시 코드
        
        [공식 문서](https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html
        )의 `Capture Video from Camera` 코드와 동일한 코드 입니다

        실행해보시면 본인의 노트북 환경에 있는 카메라의 비디오 화면이 뜰 거예요

        - 창을 x 표시하는 게 아니라 키보드의 "q" 버튼을 눌러야 종료됩니다

    - `main.py`: main.py 실행했을 때, 다음과 같이 카메라 스트리밍 화면이 뜨고, 결과가 나오도록 해주세요
        - (당연히 모두 같을 필요는 없고 가위, 바위, 보를 잘 판별하고 화면에 출력되도록 하면 됩니다.)
        
        |가위|바위|보|
        |------|---|---|
        |![가위 판별 이미지](./README_image/example_scissors.png)|![바위 판별 이미지](./README_image/example_rock.png)|![보 판별 이미지](./README_image/example_paper.png)|




## 🛠 기술 스택
- **언어**: Python 3.11+
- **AI Framework**: MediaPipe (Hand Landmarker)
- **컴퓨터 비전**: OpenCV
