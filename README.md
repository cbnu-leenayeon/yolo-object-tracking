# 휴지·스테이플러·계산기 객체 탐지 및 추적

직접 촬영한 사진으로 학습한 **로컬 YOLOv8n**과 **Roboflow YOLO11s**를 사용해 세 객체를 탐지·추적한다.
영상에 탐지 박스·클래스·신뢰도·추적 ID·중심점·이동 궤적을 표시하고, 결과 영상과 좌표 CSV를 저장한다.

## 결과 영상

두 모델 모두 같은 원본 영상 `videos/input/test_video.mp4`(1920×1080, 30 FPS, 368프레임, 약 12.27초)을 처리했다.
추적 조건은 BoT-SORT, `conf=0.1`, `imgsz=640`으로 동일하다.
아래는 README 재생용 H.264 압축본이며, 원본 해상도·FPS·전체 프레임 수를 유지했다.

### 로컬 YOLOv8n — 전체 영상

https://github.com/user-attachments/assets/c56f98c1-1069-4c3a-b155-6f248468e251

[전체 좌표 CSV](results/yolov8n/full/trajectories.csv) · [실행 설정](results/yolov8n/full/run_config.json)

### Roboflow YOLO11s — 전체 영상

https://github.com/user-attachments/assets/11196943-88c3-4591-9c1f-0d96eebb81f1

[전체 좌표 CSV](results/yolo11s/full/trajectories.csv) · [실행 설정](results/yolo11s/full/run_config.json)

README에는 전체 영상만 표시하며, 제출용 5초·전체 결과 영상과 CSV는 `results/`에 보존했다.
각 결과 폴더의 `run_config.json`에 실행 설정과 생성 경위를 기록했다.

## 데이터와 학습 방법

사진과 영상은 모두 직접 촬영했으며, 두 실험은 **동일한 원본 사진 1,208장**을 사용했다.

| 항목 | 로컬 YOLOv8n | Roboflow YOLO11s |
|---|---|---|
| train / validation / test | 903 / 305 / 별도 없음 | 846 / 242 / 120 |
| 데이터 준비 | GPT 보조, 연사 묶음 단위 분할 | 자동 라벨링, 70/20/10% 비율 분할 |
| 클래스 ID 0 / 1 / 2 | tissue / stapler / calculator | calculator / stapler / tissue |
| 설정상 최대 epoch | 50 | 300 |
| 저장된 epoch 기록 / 최고 mAP50–95 epoch | 41 / 31 | 108 / 104 |
| batch / imgsz | 8 / 640 | 32 / 640 |
| patience / optimizer 기록 | 10 / AdamW | 90 / auto |
| 학습 Ultralytics 버전 | 8.4.216 | 8.4.55 |

YOLO11s는 약 100 epoch 시점에 충분히 학습되었다고 판단해 수동 중단했으며, 다운로드 파일에는 108 epoch까지 기록되어 있다.
클래스 번호가 서로 다르므로 모델 비교는 클래스 이름으로 대응시킨다.

- **YOLOv8n 증강:** HSV 색상 변형, 이동, 크기 변형, 좌우 반전, Mosaic. [저장된 설정](training/yolov8n/train_args.checkpoint.json)
- **YOLO11s 전처리·증강:** Auto-Orient, 640×640 Stretch Resize 및 학습 중 Flip·Brightness·Blur·Mosaic·Saturation·Hue·Grayscale·Affine. [Roboflow v1 Training Recipe](https://app.roboflow.com/s-workspace-iybki/my-first-project-kqe4e/1)

YOLO11s의 온라인 증강은 Training Recipe 화면을 근거로 기록했다. checkpoint의 해당 Ultralytics 인자 값이 0이어도 증강 미적용을 뜻하지 않는다.
로컬 [분할 보고서](datasets/yolov8n/split_review.md)와 [데이터 점검 기록](training/dataset_audit.json)에 분할·라벨 차이를 보존했다.

## 학습 당시 검증 성능

| 지표 | YOLOv8n best | YOLO11s best |
|---|---:|---:|
| Precision | 87.430% | 97.661% |
| Recall | 73.870% | 97.826% |
| mAP50 | 80.810% | 99.153% |
| mAP50–95 | 58.604% | 96.611% |

저장된 checkpoint 지표와 학습 CSV를 대조한 값이다. 두 실험은 평가 분할·라벨·증강·학습 조건이 달라 **모델 구조만의 성능 차이로 해석할 수 없다.**
Roboflow는 같은 촬영 시각 접두사가 여러 split에 포함되어 유사 장면 유입 가능성이 있으며, test 120장의 별도 평가 기록은 확인되지 않았다.
YOLO11s의 클라우드 평가 데이터와 현재 export 파일의 정확한 대응도 미확인이다.

[YOLOv8n 학습 그래프](results/yolov8n/results.png) · [YOLO11s 학습 그래프](results/yolo11s/training_metrics.png)

## 실행 방법

프로젝트 루트에서 실행한다. GPU 실행에는 CUDA 지원 PyTorch 환경이 필요하며, CPU는 `--device cpu`를 추가한다.

```powershell
python -m pip install -r requirements.txt

python track_video_assignment.py --model weights/yolov8n/best.pt --name yolov8n_5s --no-preview
python track_video_assignment.py --model weights/yolo11s/best.pt --name yolo11s_5s --no-preview
```

기본 입력은 `videos/input/test_video.mp4`, 처리 길이는 5초다. 전체 영상은 `--seconds 0`을 추가한다.
결과는 `runs/track/<name>/`에 저장되며, 같은 이름이 있으면 새 번호의 폴더를 만든다.

| 출력 | 내용 |
|---|---|
| `tracking.mp4` | 원본 FPS의 무음 결과 영상, 최근 30개 연속 관측의 중심점 궤적 |
| `trajectories.csv` | 처리 구간 전체의 프레임·시간·추적 ID·클래스·신뢰도·중심점·박스 크기 |
| `run_config.json` | 실행 옵션·파일 해시·처리 프레임 수·종료 이유 |

YOLOv8n 설정 기반 재학습: `python training/yolov8n/train.py --device 0`.
이 코드는 저장된 설정으로 나중에 구성한 재현용 코드이며 최초 학습 원본은 아니다. YOLO11s는 Roboflow 웹에서 학습했다.

## 결과 관찰과 한계

두 모델 모두 일부 구간에서 같은 물체의 추적 ID가 바뀌거나 탐지가 끊겼다.
표본 영상에서는 주변 물체까지 포함한 박스와, 손에 가려져 축소된 박스도 관찰되었다.
**클래스를 올바르게 탐지하는 것과 동일 객체의 ID를 유지하는 것은 별개의 성능이다.**
ID는 강제로 고정하지 않았으며, 관측이 끊긴 구간의 궤적은 연결하지 않는다.
CSV는 예측 기록이고, 프레임별 정답 궤적이 없어 정확한 ID-switch 수나 영상 recall은 평가하지 않았다.

## 제출 자료 위치

| 경로 | 내용 |
|---|---|
| `datasets/<모델>/` | 이미지·라벨·data.yaml |
| `weights/<모델>/best.pt` | 학습한 가중치 |
| `training/<모델>/` | 학습 설정·CSV·모델 정보 |
| `results/<모델>/5s/`, `full/` | 제출 영상·좌표 CSV·실행 설정 |
| `videos/input/test_video.mp4` | 원본 테스트 영상 |

파일 출처와 정리 과정의 상세 기록은 [제출 검토 기록](training/submission_review.md)에 보존했다.
