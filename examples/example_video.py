import cv2
if __name__ == "__main__":
    import argparse

    def parse_args():
        parser = argparse.ArgumentParser(description="Video processing example")
        parser.add_argument("--video_source", type=int, default=0, help="Video source (default: 0 for webcam)")
        return parser.parse_args()

    args = parse_args()
    
    # Initialize video capture
    cap = cv2.VideoCapture(args.video_source)
    if not cap.isOpened():
        print("Error: Could not open video source.")
        exit(1)

    idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        idx += 1

        # Display the frame
        cv2.imshow("Video Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break