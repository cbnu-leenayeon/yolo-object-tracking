# YOLOv8 Object Tracking

머신러닝 과제로 진행한 휴지·스테이플러·계산기 객체 탐지 및 추적 프로젝트입니다.

## 데이터셋

직접 촬영한 이미지를 연사 묶음 단위로 분리했습니다.

- 학습 이미지 903장
- 검증 이미지 305장
- 클래스 tissue, stapler, calculator

데이터셋 구성에는 ChatGPT/Codex의 도움을 받았습니다.

## 학습 결과

YOLOv8n을 최대 50에포크로 설정해 학습했습니다.
41에포크에서 조기 종료되었으며, 31에포크의 최적 모델을 사용합니다.

- 전체 mAP50 80.8%
- 전체 mAP50–95 58.6%

## 객체 추적 영상  

https://github.com/user-attachments/assets/1c7a29c5-32e7-418d-a7ff-e7ecd20b03e9


## 실행

Ultralytics가 설치된 Python 환경에서 사용합니다.
track_video.py의 source를 입력 영상 경로로 지정한 뒤 실행합니다.

`python track_video.py`

모델 경로는 `runs/detect/three_class_train/weights/best.pt`입니다.

## 구현 현황

- 객체 탐지 및 ID 기반 추적
- 이동 궤적 시각화와 좌표 파일 저장은 추가 구현 예정
