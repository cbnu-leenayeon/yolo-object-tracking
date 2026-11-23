import argparse
from collections import defaultdict, deque
import csv
import hashlib
import json
import math
from pathlib import Path


def file_sha256(path): # 파일 내용을 식별하기 위한 해시값 계산
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_input(root, value): # 입력 파일 경로와 파일 존재 여부 확인
    path = Path(value)
    path = path if path.is_absolute() else root / path
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    return path


def new_run_folder(parent, name): # 기존 결과를 덮어쓰지 않도록 새 폴더 생성
    parent.mkdir(parents=True, exist_ok=True)
    for number in range(10000):
        path = parent / (name if number == 0 else f"{name}_{number}")
        try:
            path.mkdir()
            return path
        except FileExistsError:
            continue
    raise RuntimeError("Too many existing runs with this name.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="weights/yolov8n/best.pt") # 학습한 모델 경로
    parser.add_argument("--source", default="videos/input/test_video.mp4") # 원본 영상 경로
    parser.add_argument("--name", default="assignment_tracking") # 결과 폴더 이름
    parser.add_argument("--output-dir", default="runs/track", help="Directory for a new run folder")
    parser.add_argument("--seconds", type=float, default=5. 0, help="0 = complete video") # 0이면 전체 영상 처리
    parser.add_argument("--tracker", default="botsort.yaml") # 사용할 추적기 설정
    parser.add_argument("--conf", type=float, default=0.1) # 탐지 신뢰도 기준
    parser.add_argument("--imgsz", type=int, default=640) # 모델 입력 이미지 크기
    parser.add_argument("--device", default="0", help="0 = first GPU; cpu = CPU")
    parser.add_argument("--no-preview", action="store_true") # 미리보기 없이 결과 저장
    args = parser.parse_args(argv)

    if not math.isfinite(args.seconds) or args.seconds < 0:
        parser.error("--seconds must be a finite number >= 0")
    if not 0 <= args.conf <= 1 or args.imgsz <= 0:
        parser.error("--conf must be 0..1 and --imgsz must be positive")
    if not args.name or Path(args.name).name != args.name or args.name in (".", "..") or "/" in args.name or "\\" in args.name:
        parser.error("--name must be a folder name, without a path")

    import cv2
    import numpy as np
    import ultralytics
    from ultralytics import YOLO

    root = Path(__file__).resolve().parent # 이 파이썬 파일이 있는 폴더를 기준 경로로 사용
    model_path = resolve_input(root, args.model)
    source_path = resolve_input(root, args.source)
    model = YOLO(str(model_path)) # 학습된 가중치 불러오기

    print("Classes:", model.names)
    print("Tracker:", args.tracker)
    print("Use the unannotated source video as input.")

    cap = cv2.VideoCapture(str(source_path)) # 입력 영상 열기
    if not cap.isOpened():
        cap.release()
        raise RuntimeError("Cannot open input video.")

    fps = float(cap.get(cv2.CAP_PROP_FPS)) # 원본 영상의 FPS 확인
    if not math.isfinite(fps) or fps <= 0:
        cap.release()
        raise RuntimeError("Cannot determine video FPS.")

    limit = max(1, round(args.seconds * fps)) if args.seconds else None # 처리할 최대 프레임 수 계산
    output_parent = Path(args.output_dir)
    if not output_parent.is_absolute():
        output_parent = root / output_parent

    run = new_run_folder(output_parent, args.name)
    video_path, csv_path = run / "tracking.mp4", run / "trajectories.csv"
    histories = defaultdict(lambda: deque(maxlen=30)) # 객체별 최근 중심점 30개 저장
    last_seen = {} # 객체가 마지막으로 관측된 프레임 기록
    palette = [(0, 220, 0), (255, 180, 0), (0, 180, 255), (255, 0, 200)] # 궤적 색상이며 BGR 순서
    writer = None
    frame_index = 0
    stop_reason = "duration_limit"
    preview = not args.no_preview

    config = dict(
        vars(args),
        model=str(model_path),
        source=str(source_path),
        ultralytics_version=ultralytics.__version__,
        fps=fps,
        model_sha256=file_sha256(model_path),
        source_sha256=file_sha256(source_path),
        class_names=model.names,
    ) # 실행 설정과 입력 파일 정보를 기록
    config["timestamp_note"] = "time_seconds is frame_index / source FPS; nominal for variable-FPS sources"
    config["notes"] = "Video is silent. Tracker IDs are not forced or relabeled. CSV is a prediction log."

    try:
        with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
            rows = csv.writer(handle)
            rows.writerow([
                "frame_index", "time_seconds", "track_id", "class_id", "class_name",
                "confidence", "center_x", "center_y", "width", "height",
            ]) # CSV에 저장할 항목 이름

            while limit is None or frame_index < limit:
                ok, frame = cap.read() # 영상에서 다음 프레임 읽기
                if not ok:
                    stop_reason = "source_end"
                    break

                result = model.track(
                    frame,
                    persist=True,
                    tracker=args.tracker,
                    conf=args.conf,
                    imgsz=args.imgsz,
                    device=args.device,
                    verbose=False,
                )[0] # 연속 프레임 사이에서 추적 상태 유지

                annotated = result.plot() # 탐지 박스·이름·신뢰도·추적 ID 표시
                boxes = result.boxes

                if boxes is not None and len(boxes):
                    centers = boxes.xywh.cpu().tolist() # 박스 중심 좌표와 너비·높이
                    classes = boxes.cls.int().cpu().tolist() # 클래스 번호
                    scores = boxes.conf.cpu().tolist() # 탐지 신뢰도
                    ids = boxes.id.int().cpu().tolist() if boxes.id is not None else [None] * len(centers)

                    for center, class_id, score, track_id in zip(centers, classes, scores, ids):
                        x, y, width, height = map(float, center)

                        rows.writerow([
                            frame_index,
                            round(frame_index / fps, 6),
                            "" if track_id is None else track_id,
                            class_id,
                            result.names[class_id],
                            score,
                            x, y, width, height,
                        ]) # 현재 프레임의 객체별 예측 결과 저장

                        if track_id is None:
                            continue # 추적 ID가 없는 탐지는 궤적 표시 생략

                        history_key = (track_id, class_id)
                        history = histories[history_key]

                        if history_key in last_seen and last_seen[history_key] != frame_index - 1:
                            history.clear() # 관측이 끊긴 구간을 임의의 선으로 연결하지 않음

                        history.append((x, y))
                        last_seen[history_key] = frame_index
                        color = palette[class_id % len(palette)] # 같은 클래스의 궤적은 같은 색 사용
                        cv2.circle(annotated, (round(x), round(y)), 4, color, -1) # 현재 중심점 표시

                        if len(history) >= 2:
                            points = np.asarray(history, dtype=np.int32).reshape((-1, 1, 2))
                            cv2.polylines(annotated, [points], False, color, 3) # 최근 중심점들을 연결해 궤적 표시

                if writer is None:
                    height, width = annotated.shape[:2]
                    writer = cv2.VideoWriter(
                        str(video_path),
                        cv2.VideoWriter_fourcc(*"mp4v"),
                        fps,
                        (width, height),
                    ) # 원본 FPS로 결과 영상 저장
                    if not writer.isOpened():
                        raise RuntimeError("Cannot create output MP4.")

                writer.write(annotated)
                frame_index += 1

                if frame_index == 1 or frame_index % 30 == 0:
                    print(f"Processed: {frame_index} frames", flush=True)

                if preview:
                    try:
                        height, width = annotated.shape[:2]
                        scale = min(1.0, 1280 / width, 720 / height) # 미리보기 크기를 화면에 맞게 축소
                        shown = cv2.resize(
                            annotated,
                            (round(width * scale), round(height * scale)),
                        )
                        cv2.imshow("Assignment tracking - Q stops early", shown)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            stop_reason = "user_quit"
                            break # Q 키를 누르면 처리 조기 종료
                    except cv2.error:
                        preview = False # 미리보기 오류가 발생해도 저장은 계속 진행
                        print("Preview unavailable; output saving continues.")

        if frame_index == 0:
            raise RuntimeError("No source frames could be decoded.")

        config["status"] = "completed"

    except Exception:
        config["status"] = "failed"
        raise

    finally:
        cap.release() # 입력 영상 자원 해제
        if writer is not None:
            writer.release() # 영상 저장 마무리

        try:
            cv2.destroyAllWindows()
        except cv2.error:
            pass

        config.update(
            processed_frames=frame_index,
            saved_seconds=frame_index / fps,
            stop_reason=stop_reason,
        )
        (run / "run_config.json").write_text(
            json.dumps(config, ensure_ascii=False, indent=2),
            encoding="utf-8",
        ) # 정상 종료와 오류 발생 모두 실행 기록 저장

    print(f"Video: {video_path}")
    print(f"Trajectory CSV: {csv_path}")
    print(f"Saved duration: {frame_index / fps:.3f} seconds")

    if limit is not None and frame_index < limit:
        print("WARNING: Saved clip is shorter than the requested duration.")

    print("ID changes remain visible. persist=True does not guarantee identity recovery after occlusion.")


if __name__ == "__main__":
    main() # 파일을 직접 실행했을 때 시작