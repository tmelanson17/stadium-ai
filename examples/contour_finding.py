import argparse
import cv2

def parse_args():
    parser = argparse.ArgumentParser(description="Find contours in an image.")
    parser.add_argument("image_path", type=str, help="Path to the input image")
    parser.add_argument("--min_area", type=int, default=1000, help="Minimum area of contours to consider")
    parser.add_argument("--max_area", type=int, default=50000, help="Maximum area of contours to consider")
    return parser.parse_args()

def main(args: argparse.Namespace):
    # Load the image
    image = cv2.imread(args.image_path)
    if image is None:
        print(f"Error: Could not load image from {args.image_path}")
        return

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Use negative image for contour detection
    gray = cv2.bitwise_not(gray)

    # Find contours
    contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        # Print contour area for debugging
        area = cv2.contourArea(cnt)
        print(f"Contour area: {area}")

    # Filter contours based on area
    filtered_contours = [cnt for cnt in contours if args.min_area < cv2.contourArea(cnt) < args.max_area]

    # Draw contours on the original image
    cv2.drawContours(image, filtered_contours, -1, (0, 255, 0), 3)

    # Show the result
    cv2.imshow("Contours", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    args = parse_args()
    main(args)