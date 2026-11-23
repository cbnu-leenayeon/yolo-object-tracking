# Roboflow YOLO11s 학습 기록

실제 다운로드한 가중치의 모델 구성은 yolo11s.yaml, scale=s, 3개 클래스다.
train_args.checkpoint.json과 results.csv는 가중치 내부의 학습 설정과 기록에서 추출했다.
최대 300 epoch, patience 90, batch 32, imgsz 640이다. 내장 기록은 108 epoch까지 있고 최고 mAP50–95는 104 epoch다.
전체 학습 종료 epoch와 종료 이유는 확인 필요다. 108 epoch에서 조기 종료되었다고 단정할 근거는 없다.
Roboflow 서비스의 원본 학습 코드는 다운로드 자료에 포함되지 않았다. 원본 코드·GPU 종류는 확인 필요다.
데이터셋 v1 export의 클래스 순서는 가중치와 같고 사용자 프로젝트에 함께 저장되어 있다.
체크포인트의 데이터 경로는 /train/cache/dataset/data.yaml이며 export 버전 ID나 해시가 없어, 클라우드 학습 당시 정확한 데이터 버전 연결은 확인 필요다.
현재 포함한 export의 실제 train/valid/test 파일은 변경 없이 보존했다.
