# 제출 정리 검토 기록

## 보존과 변경

프로젝트 루트의 README.md, .gitignore, track_video_assignment.py 원문은 archive/before_submission_20261123_095323/에 보존했다.
기존 파일 10,397개의 원래 위치 또는 이동 후 위치와 크기를 대조했다.
데이터셋·가중치·결과 등 4,852개 복사 파일은 원본과 SHA-256이 같은지 확인했다.
원본 입력 영상 10개는 처음·중간·마지막 프레임을 확인한 뒤 videos/input/으로 이동하고 해시를 확인했다.
초기 yolov8n.pt는 COCO 80개 클래스 사전 학습 모델이며 training/yolov8n/yolov8n.pt에도 보존했다.
기존 분할 보고서는 datasets/yolov8n/에 복사했고 원본 자료는 archive에도 보존했다.

공통 추적 코드의 기본 모델은 weights/yolov8n/best.pt, 기본 입력은 videos/input/test_video.mp4다.
기존 5초·전체 처리, 원본 FPS, 박스·클래스·신뢰도·ID·중심점·궤적·CSV를 유지했다.
동일 ID가 다른 클래스로 나타날 때 궤적을 연결하지 않도록 (track_id, class_id)별로 기록한다.
새 실행에는 모델·원본 영상 SHA-256과 클래스 이름을 함께 저장한다.

## 실험 연결 근거

| 항목 | YOLOv8n | YOLO11s |
|---|---|---|
| 가중치 원본 | runs/detect/three_class_train/weights/best.pt | 기존 weights/roboflow_yolo11s.pt |
| 모델 내부 확인 | yolov8n.pt 학습 인자, C2f, depth 0.33, width 0.25 | yolo11s.yaml, scale=s, C3k2·C2PSA |
| 데이터 근거 | 학습 args의 burst_split/data.yaml과 기존 이미지·라벨 manifest 해시 일치 | Roboflow v1 export와 가중치 클래스 순서 일치 |
| 데이터 구성 | train 903, val 305 | train 846, valid 242, test 120 |
| 가중치 학습 기록 | 최고 31, 기록 41 epoch | 최고 104, 내장 기록 108 epoch |
| 결과 실행 근거 | runs/track/assignment_yolov8n/run_config.json | runs/track/assignment_yolo11s/run_config.json |
| 결과 영상 확인 | 368프레임, 30 FPS, 1920×1080 | 368프레임, 30 FPS, 1920×1080 |

다운로드 Roboflow 가중치와 기존 weights.pt는 동일 SHA-256이다.
기존 결과 설정에 가중치 해시는 기록되지 않아, 모델 경로와 클래스 대응 및 영상 메타데이터로 연결했다.
results의 이동 후 설정에 기록한 해시는 정리 시점의 값이다.
클라우드 checkpoint의 데이터 경로에는 export 버전 ID가 없어 정확한 학습 당시 데이터 버전 연결은 확인 필요다.
기록이 108 epoch까지 있다는 사실만으로 전체 종료 epoch나 조기 종료 이유를 확정하지 않았다.

## 유지한 분할과 라벨

두 데이터셋 총 2,416장과 대응 TXT 2,416개를 보존했다. split 사이 동일 파일 해시 중복은 각각 0개다.
Roboflow에서는 같은 촬영 시각 접두사 18개가 여러 split에 걸쳐 있어 유사 장면의 중복 유입 가능성을 README에 명시했다.
기존 실험의 분할을 재구성하거나 증강 이미지를 새로 만들지 않았다.
Roboflow의 클래스 번호 0=calculator, 1=stapler, 2=tissue와 YOLOv8n의 0=tissue, 1=stapler, 2=calculator를 각각 유지했다.
Roboflow의 이미지당 복수 객체 라벨도 유지했고, 클래스별 이미지·박스 수를 dataset_audit.json에 기록했다.

## 출처가 불분명하거나 현재 실험에서 사용하지 않는 자료

| 위치 | 판단과 보존 |
|---|---|
| archive/before_submission_20261123_095323/legacy/roboflow_result.mp4 및 roboflow_predictions.jsonl | JSONL 원본 영상 해시는 현재 test_video.mp4와 일치. Cloud workflow와 다운로드 best.pt의 동일 가중치 여부 확인 필요. archive에 보존 |
| runs/detect/runs/detect/video_check* | 실행 설정·가중치 해시가 없어 모델 연결 확인 필요. 원래 runs에 보존 |
| runs/detect/runs/track/* | 파일명만으로 분류하지 않고 원래 runs에 보존. 특히 yolo8/yolo11 이름의 과거 영상은 정확한 모델·설정 확인 필요 |
| runs/track/test_video_20261123_010556_995788 | 모델과 실행 설정 연결 확인 필요. 원래 runs에 보존 |
| archive/before_submission_20261123_095323/legacy/dataset_tissue_stapler_calculator_burst_split/images2 | 학습 args와 YAML이 참조하는 images와 별도인 중간 사본. 원래 폴더를 archive에 보존 |
| archive/before_submission_20261123_095323/legacy/dataset_tissue_stapler_calculator | 이전 분할 자료. 실제 three_class_train의 data 인자는 burst_split 폴더를 가리킴. 원문 보존 |
| archive/before_submission_20261123_095323/legacy/dateset | 초기 watch 준비 자료. 현재 두 세 클래스 실험과 별도 보관 |
| archive/before_submission_20261123_095323/legacy/track_video_*.py 및 Roboflow 관련 코드 | 기존 코드 원문 보존. 일부 입력 경로 누락·문법 오류를 새 통합 코드에서 해소 |
| archive/before_submission_20261123_095323/legacy 내 API 관련 코드와 복구 자료 | archive에 보존하고 Git에서 제외. 민감 내용은 새 코드·문서로 옮기지 않음 |

## 검증 범위

- 제출 실행 코드와 재현 코드의 AST 문법 및 --help 실행 확인.
- 실제 YAML 상대 경로와 이미지·라벨 파일명 대응, 클래스 번호·이름 대조.
- 두 최종 가중치와 결과 영상·CSV·실행 설정의 경로·해시·클래스 대조.
- 모의 탐지 입력으로 30 FPS의 기본 5초 영상 150프레임 저장, 전체 처리 170프레임 저장, CSV, 원래 ID 유지, 클래스가 다른 동일 ID의 궤적 분리 확인.
- 실제 GPU 추론, 재학습, Roboflow API 호출은 실행하지 않음.
- 기존 최종 영상의 표본 프레임과 전체 CSV 로그를 읽어 비교함. 프레임별 정답이 없어 오탐률·정확한 ID-switch 수는 확인 필요.
- Roboflow 서비스 원본 학습 코드, 클라우드 GPU, test 평가, 전체 학습 종료 이유와 일부 원본 실행 명령은 확인 필요.

## Git과 용량

시작과 종료의 HEAD는 0f1e435fac795b07b1908c2c88616e3d22f06b55로 같다.
커밋·push·이력 재작성·LFS 변환을 실행하지 않았다.
기존 사용자 작업의 track_video.py 삭제 상태를 유지했다.
README와 .gitignore의 수정, 새 폴더·코드는 검토 가능한 작업 트리 변경으로 남겼다.
runs의 기존 추적 파일 9개는 디스크를 보존하며 Git 인덱스에서 제외했으며 staged 삭제로 보인다.
Git 인덱스 변경 전 사본은 원문 백업 폴더의 git-index.before-exclusion에 보관했다.
기존 분할 보고서의 이전 경로는 archive로 이동해 Git에서는 삭제로 보이며, 새 datasets 위치에 원문이 포함된다.

원본 폴더 archive, runs, videos/input과 가상환경·캐시·환경변수 파일은 제외 규칙 검사를 통과했다.
datasets, weights, results의 제출 자료와 코드·설정 파일은 포함 대상임을 확인했다.
검증 시점 제출 파일 용량은 4,259,339,385 bytes, 약 4.26 GB (3.97 GiB)다.
이 보고서 생성 후 용량에는 작은 텍스트 파일 크기만 추가된다.
최대 개별 파일은 weights/yolo11s/best.pt의 19,185,882 bytes (18.30 MiB)다. 50 MiB를 넘는 제출 파일은 0개다.
Git LFS 3.7.1 설치를 확인했다. 데이터셋 전체를 유지하며 LFS를 선택하는 절차는 README에 제시했고 실제 적용은 검토 단계로 남겼다.


## 최종 영상 제출 범위 갱신

원본 videos/input/test_video.mp4와 results/<모델>/5s/·full/의 영상 네 개를 제출한다. 각 결과의 CSV와 설정을 함께 포함한다.
번호가 붙은 원본 영상과 다른 기존 결과 영상은 같은 로컬 경로에 보존하며 Git에서 제외한다. 위 초기 검증 시점의 videos/input 전체 제외 규칙은 test_video.mp4 예외를 포함하는 규칙으로 갱신했다.
YOLOv8n 5초 실행은 7프레임의 불완전 결과라, 완료된 full 영상 앞 150프레임과 대응 CSV 행에서 제출용 5초 결과를 파생했다. 새 모델 추론은 실행하지 않았다.
구체적인 영상 경로·프레임 수·SHA-256은 training/final_video_manifest.json과 각 결과 run_config.json에 기록했다.
