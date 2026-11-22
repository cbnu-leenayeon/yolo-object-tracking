from ultralytics import YOLO

# 학습한 모델 불러오기
model = YOLO("runs/detect/three_class_train/weights/best.pt")

# 영상에서 객체 추적하고 결과 영상 저장하기
model.track(
    source="test_video_best.mp4",
    save=True,
    device=0,
    project="runs/track",
    name="basic_tracking",
)