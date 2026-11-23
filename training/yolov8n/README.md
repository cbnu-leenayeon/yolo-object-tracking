# YOLOv8n 학습 기록

원본 실행 기록은 args.original.yaml, results.original.csv에 보존했다.
체크포인트에는 최종 적용된 optimizer=AdamW가 남아 있고 원본 args에는 optimizer=auto가 기록되어 있다.
최대 50 epoch, patience 10으로 학습했으며 기록은 41 epoch까지 있고 최고 mAP50–95는 31 epoch다.
train.py는 정리 과정에서 저장된 설정을 바탕으로 구성한 재현용 코드다. 최초 학습에 사용한 원본 실행 명령·스크립트는 확인 필요다.
data.original.yaml과 checkpoint_metadata.json에는 이동 전 경로가 남아 있다. 현재 데이터 경로는 datasets/yolov8n/data.yaml이다.
