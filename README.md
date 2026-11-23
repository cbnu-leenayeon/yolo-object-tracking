# 휴지·스테이플러·계산기 객체 탐지 및 추적

머신러닝 과제에서 직접 촬영한 세 객체를 탐지하고 추적하는 프로젝트다.
로컬에서 처음 학습한 YOLOv8n과 Roboflow에서 학습하여 다운로드한 YOLO11s를 보존하고 비교한다.
데이터 분할, 라벨, 증강과 학습 조건이 달라 아래 점수 차이는 실험 전체의 차이로 해석한다.

## 폴더 구성

```text
README.md
requirements.txt
.gitignore
track_video_assignment.py
training/
  yolov8n/             # 원본 설정·학습 기록과 설정 기반 재현 코드
  yolo11s/             # 다운로드 가중치에서 추출한 Roboflow 학습 기록
  dataset_audit.json
  file_provenance.json
  submission_review.md
datasets/
  yolov8n/             # images/train, images/val, labels와 data.yaml
  yolo11s/             # train, valid, test의 images·labels와 data.yaml
weights/
  yolov8n/best.pt
  yolo11s/best.pt
videos/input/          # test_video.mp4만 제출, 번호가 붙은 원본은 로컬 보존
results/
  yolov8n/             # 5s/·full/ 최종 영상·CSV·설정과 대표 검증 그래프
  yolo11s/             # 5s/·full/ 최종 영상·CSV·설정과 내장 기록 그래프
runs/                 # 자동 생성된 전체 실행 기록, Git 제외
archive/              # 이전 코드·중간 자료·정리 전 파일, Git 제외
```

## 데이터셋

| 항목 | YOLOv8n | Roboflow YOLO11s |
|---|---|---|
| train | 903장, 74.75% | 846장, 70.03% |
| validation | 305장, 25.25% | 242장, 20.03% |
| test | 별도 분할 없음 | 120장, 9.93% |
| 합계 | 1,208장 | 1,208장 |
| 클래스 ID 0 / 1 / 2 | tissue / stapler / calculator | calculator / stapler / tissue | 

## 모델과 학습 조건

| 항목 | 로컬 YOLOv8n | Roboflow YOLO11s |
|---|---|---|
| 확인 근거 | checkpoint의 yolov8n.pt와 C2f 모델 구성 | yolo11s.yaml, scale=s, C3k2·C2PSA 구성 |
| 최대 epoch | 50 | 300 |
| patience | 10 | 90 |
| batch | 8 | 32 |
| imgsz | 640 | 640 |
| optimizer | 원본 args는 auto, checkpoint 적용값은 AdamW | auto |
| 기록 범위 | 1~41 epoch | 내장 기록 1~108 epoch |
| 최고 mAP50–95 epoch | 31 | 내장 기록 중 104 |
| 학습 종료 | 41 epoch, 최고 기록 후 patience 10과 일치 | 100 epoch |
| 학습 소프트웨어 | Ultralytics 8.4.216 | checkpoint의 Ultralytics 8.4.55 |
| 학습 GPU | 기존 과제 기록의 RTX 4060 Laptop GPU, args의 device=0 | 확인 필요 |

YOLOv8n 증강 설정은 hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, translate=0.1, scale=0.5, fliplr=0.5, mosaic=1.0, close_mosaic=10이다.
Roboflow checkpoint에서는 hsv, 이동·크기·회전·반전, mosaic, mixup, copy_paste, erasing이 모두 0으로 기록되어 있다.
전체 설정은 training/<모델>/train_args.checkpoint.json에 보존했다.

weights/yolov8n/best.pt는 runs/detect/three_class_train/weights/best.pt에서 복사했다.
weights/yolo11s/best.pt는 weights/roboflow_yolo11s.pt에서 복사했고 루트의 weights.pt와도 해시가 같았다.
기존 루트 yolov8n.pt는 COCO 80개 클래스를 갖는 초기 사전 학습 가중치로 확인했다.
모델 구성과 SHA-256은 training/<모델>/checkpoint_metadata.json에 기록했다.

최초 학습 실행 명령 원본은 확인 필요다. training/yolov8n/train.py는 정리 과정에서 저장된 설정으로 구성한 재현용 코드다.
Roboflow 서비스의 실제 학습 소스는 다운로드 자료에 포함되지 않아 설정과 기록을 보존했다.

## 저장된 검증 성능

| 지표 | YOLOv8n best | Roboflow YOLO11s 다운로드 best |
|---|---:|---:|
| Precision | 87.43% | 97.661% |
| Recall | 73.87% | 97.826% |
| mAP50 | 80.81% | 99.153% |
| mAP50–95 | 58.604% | 96.611% |

각 best.pt 내부 train_metrics와 내장 results 기록에서 확인한 값이다.
YOLOv8n은 로컬 validation 305장에 대한 학습 당시 평가다.
YOLO11s는 클라우드 validation 수치이며 현재 export validation 242장과 평가 당시 파일의 해시 연결은 확인 필요다.
test 120장에 대한 별도 평가 기록은 확인 필요다.
두 점수의 차이에는 분할 독립성, 라벨 구성, 증강, batch, 학습 기간과 모델 크기가 함께 영향을 줄 수 있다.
대표 그래프는 results/yolov8n/results.png와 results/yolo11s/training_metrics.png다.
YOLO11s 그래프는 다운로드 가중치 안의 108개 epoch 기록을 그렸다.

## 실행 방법

```powershell
python -m pip install -r requirements.txt
```

확인한 로컬 환경은 Ultralytics 8.4.216, PyTorch 2.11.0+cu128, torchvision 0.26.0+cu128, OpenCV 4.12.0.88, NumPy 2.2.6이다.
requirements.txt의 PyTorch 버전은 CUDA 빌드 접미사를 제외했다. GPU 실행에는 호환되는 CUDA 지원 PyTorch 환경이 필요하다.
원본 videos/input/test_video.mp4를 GitHub에 포함한다. test_video2.mp4부터 test_video10.mp4까지의 번호가 붙은 영상은 로컬에 보존하고 Git에서 제외한다.
상대 경로는 코드 파일이 있는 프로젝트 루트를 기준으로 해석한다.

```powershell
python track_video_assignment.py --model weights/yolov8n/best.pt --source videos/input/test_video.mp4 --name yolov8n_5s --no-preview
python track_video_assignment.py --model weights/yolo11s/best.pt --source videos/input/test_video.mp4 --name yolo11s_5s --no-preview
```

기본 처리 길이는 5초, 기본 모델은 YOLOv8n이다. 전체 영상에는 --seconds 0을 사용한다.

```powershell
python track_video_assignment.py --model weights/yolov8n/best.pt --source videos/input/test_video.mp4 --name yolov8n_full --seconds 0 --no-preview
python track_video_assignment.py --model weights/yolo11s/best.pt --source videos/input/test_video.mp4 --name yolo11s_full --seconds 0 --no-preview
```

기본 출력은 runs/track/<name>/의 tracking.mp4, trajectories.csv, run_config.json이다.
같은 이름이 있으면 새 번호의 폴더를 만든다. --output-dir results/yolov8n처럼 출력 상위 폴더를 지정할 수 있다.
--device cpu로 CPU를 선택할 수 있다. 기본 device는 0, tracker는 botsort.yaml, conf는 0.1, imgsz는 640이다.

탐지 박스, 클래스, 신뢰도, ID, 중심점과 최근 30개 관측의 궤적을 표시하고 원본 FPS로 무음 영상을 저장한다.
CSV는 프레임·시간·ID·클래스·신뢰도·중심점·박스 크기를 기록한다. 시간은 frame_index/FPS이며 가변 FPS에서는 명목 시각이다.
Tracker ID를 그대로 사용하고 ID와 클래스 조합별로 궤적을 관리한다. 관측이 끊기면 선을 끊는다.
ID 변경은 새 궤적으로 남으며 가림 이후 동일 객체의 ID 복원은 추적 결과에 따라 달라진다.



### 최종 제출 영상

| 모델 | 5초, 150프레임 | 전체, 368프레임 |
|---|---|---|
| YOLOv8n | results/yolov8n/5s/tracking.mp4 | results/yolov8n/full/tracking.mp4 |
| YOLO11s | results/yolo11s/5s/tracking.mp4 | results/yolo11s/full/tracking.mp4 |

모든 제출 영상은 test_video.mp4 기반이며 원본 FPS인 30 FPS를 유지한다. 각 영상 옆에 대응하는 trajectories.csv와 run_config.json을 포함했다.
YOLOv8n의 기존 5초 실행은 7프레임만 저장되어 완료된 full 결과의 앞 150프레임을 디코딩·재인코딩해 5초 영상을 만들었다.
이 5초 CSV는 full CSV의 frame_index < 150인 원래 행을 추출했다. 해당 작업에서는 새 모델 추론을 실행하지 않았다.
YOLO11s의 5초 결과와 두 full 결과는 완료된 실행 기록에서 그대로 복사했다.
기존 입력·추적·중간 영상은 원래 로컬 위치에 모두 보존하고, 업로드 포함 여부만 .gitignore로 제한했다.

## 기존 결과와 관찰

각 results/<모델>/5s/와 full/에 제출할 영상·CSV·설정을 배치했다. GitHub에 포함하는 영상은 원본 test_video.mp4와 아래 네 결과 영상이다.
두 실행은 같은 test_video.mp4, 1920×1080, 30 FPS, 368프레임의 전체 약 12.267초를 처리했다.
설정은 botsort.yaml, conf=0.1, imgsz=640이다.
제출 대상으로 선택한 실행 설정의 모델·원본 영상 SHA-256을 현재 파일과 대조했다. 각 결과 설정에는 영상·CSV 해시와 원래 실행 폴더도 기록했다.

| 해당 클래스가 CSV에 없는 프레임 수 / 368 | YOLOv8n | YOLO11s |
|---|---:|---:|
| 휴지 | 29 | 10 |
| 스테이플러 | 4 | 114 |
| 계산기 | 29 | 52 |

위 수치는 CSV 로그가 없는 프레임 수다. 프레임별 정답 주석이 없어 가림·화면 밖 이동과 실제 미탐을 분리한 recall로 해석하려면 추가 검수가 필요하다.
YOLOv8n 계산기 ID는 1·6, 휴지 ID는 3·1·11로 기록되었다.
YOLO11s 계산기는 1·6·13, 휴지는 2·1·14·15, 스테이플러는 3·4·16으로 기록되었다.
기존 영상의 처음·중간·마지막 프레임에서 ID 변경과 탐지 누락을 확인했다.
YOLO11s 첫 프레임의 스테이플러 박스는 주변 장난감 영역까지 포함해 위치 오차가 보였다.
YOLOv8n 중간 프레임에서는 손이 겹친 계산기의 박스가 일부 영역으로 줄고, 휴지에 이전 계산기 ID가 할당되는 모습이 보였다.
정확한 ID-switch 수와 오탐률은 프레임별 정답 궤적을 만든 뒤 평가해야 한다.
연결이 불명확한 다른 과거 결과는 runs/ 또는 archive/에 보존하고 확인 필요 목록에 기록했다.

## 문제와 한계

- 초기 1 epoch 점검의 mAP50은 0.121%였고 다중 epoch 학습 후 최고 기록이 개선되었다.
- Roboflow export는 클래스 순서, 라벨 구성과 분할이 로컬 데이터와 달랐다.
- 다운로드 YAML 경로를 실제 데이터 위치와 맞게 수정했다.
- 이전 실험 코드의 누락된 입력 경로와 문법 오류가 있는 파일은 archive에 원문을 보존했다.
- 원본 README·이전 코드·API 관련 코드와 민감 자료는 archive에 보관하고 Git에서 제외했다.
- Cloud 가중치와 export v1의 학습 당시 연결, 클라우드 GPU, 전체 종료 epoch·이유, test 평가와 학습 원본 코드 일부는 확인 필요다.
- 별도 분할 보고서는 datasets/yolov8n/split_review.md와 split_manifest.json에 보존했다.
- 정리 후 검증 범위와 미분류 자료는 training/submission_review.md에 기록했다.
- 이번 정리 과정에서는 GPU 추론, 재학습, Roboflow API 호출을 실행하지 않았다.

## GitHub 제출과 용량

두 데이터셋·가중치·최종 결과·실행 코드·학습 설정을 포함한다.
가상환경·캐시·환경변수·API 관련 민감 자료·runs·archive와 번호가 붙은 입력 영상은 .gitignore로 제외한다. videos/input/test_video.mp4와 모델별 5s/·full/ 결과만 영상 제출 대상으로 지정했다.
이미 추적 중이던 runs 파일은 로컬 파일을 보존하며 Git 인덱스에서 제외했다.
제출 파일별 크기와 전체 크기는 training/submission_review.md에 기록했다.
GitHub 일반 Git은 100 MiB 초과 파일을 제한하고 50 MiB 초과 파일에 경고한다. 저장소는 1 GB 미만이 이상적이며 5 GB 미만을 권장한다.
데이터셋을 포함한 상태에서 Git LFS를 선택할 수 있다. 다음은 검토 후 적용할 명령이다.

```powershell
git lfs install --local
git lfs track "datasets/yolov8n/images/**/*.jpg" "datasets/yolo11s/**/images/*.jpg" "weights/*/best.pt" "results/*/tracking.mp4"
```

LFS 용량·대역폭은 GitHub 요금제에서 확인해야 한다.
이번 정리에서는 LFS 변환, 커밋, push를 수행하지 않았다.
근거는 [GitHub 파일 크기 문서](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)와 [Git LFS 설정 문서](https://docs.github.com/en/repositories/working-with-files/managing-large-files/configuring-git-large-file-storage)다.
