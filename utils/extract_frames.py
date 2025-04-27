import cv2
import os
import argparse


def extract_frames(video_path, step, output_dir):
    """
    Extract frames from video at every `step` seconds and save to `output_dir`.
    """
    if not os.path.isfile(video_path):
        print(f"Error: Video file '{video_path}' does not exist.")
        return

    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video '{video_path}'")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        print("Warning: Unable to determine FPS, defaulting to 30")
        fps = 30.0
    frame_interval = int(round(step * fps))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Video FPS: {fps:.2f}")
    print(f"Total frames: {total_frames}")
    print(f"Extracting one frame every {step} seconds (~every {frame_interval} frames)")

    for frame_idx in range(0, total_frames, frame_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            continue
        filename = os.path.join(output_dir, f"frame_{frame_idx:06d}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Saved {filename}")

    cap.release()
    print("Done extracting frames.")


def main():
    parser = argparse.ArgumentParser(
        description="Extract frames from a video at regular time intervals."
    )
    parser.add_argument(
        "video_path",
        help="Path to the input video file."
    )
    parser.add_argument(
        "-s", "--step",
        type=float,
        default=0.5,
        help="Time interval in seconds between frames (default: 0.5)."
    )
    parser.add_argument(
        "-o", "--output",
        default="frames",
        help="Directory to save the extracted frames."
    )
    args = parser.parse_args()

    extract_frames(args.video_path, args.step, args.output)


if __name__ == "__main__":
    main()
    
# python .\utils\extract_frames.py .\static\videos\parking0001_video.mp4 --step 0.5 --output parking_dataset\001