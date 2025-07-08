from src.state_reader.tesseract import read_text_from_roi, preprocess_for_ocr
from src.state_reader.condition_reader import CONDITION_TESSERACT_CONFIG
from src.state_reader.hp_reader import HP_TESSERACT_CONFIG

import cv2
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Run Tesseract OCR on an image.")
    parser.add_argument("image_path", type=str, help="Path to the input image")
    parser.add_argument("--roi", type=str, default=None, help="Region of interest as 'x1,y1,x2,y2' (top-left and bottom-right coordinates)")
    parser.add_argument("--condition", action="store_true", help="Use condition Tesseract config")
    parser.add_argument("--hp", action="store_true", help="Use HP Tesseract config")
    parser.add_argument("--preprocess", action="store_true", help="Apply preprocessing to the image before OCR", default=False)
    return parser.parse_args()

def main(args: argparse.Namespace):
    # Load the image
    image = cv2.imread(args.image_path)
    if image is None:
        print(f"Error: Could not load image from {args.image_path}")
        return

    # Parse ROI if provided
    roi = None
    if args.roi:
        try:
            coords = list(map(int, args.roi.split(',')))
            if len(coords) != 4:
                raise ValueError("ROI must be in the format 'x1,y1,x2,y2'")
            roi = ((coords[0], coords[1]), (coords[2], coords[3]))
        except Exception as e:
            print(f"Error parsing ROI: {e}")
            return

    # Choose Tesseract config based on flags
    if args.condition and args.hp:
        print("Error: Cannot use both --condition and --hp flags at the same time.")
        return
    elif args.condition:
        tesseract_config = CONDITION_TESSERACT_CONFIG
        otsu_arg = False
        remove_noise = False
    elif args.hp:
        tesseract_config = HP_TESSERACT_CONFIG
        otsu_arg = True
        remove_noise = True
    else:
        print("Need to specify either --condition or --hp flag for Tesseract config.")
        return
    

    # Read text from ROI or entire image
    if roi:
        text = read_text_from_roi(image, roi, tesseract_config=tesseract_config, 
                                  preprocess=args.preprocess, use_otsu=otsu_arg, remove_noise=remove_noise)
    else:
        text = read_text_from_roi(image, ((0, 0), (image.shape[1], image.shape[0])), tesseract_config=tesseract_config, 
                                  preprocess=args.preprocess, use_otsu=otsu_arg, remove_noise=remove_noise)

    print("Detected text:", text)
    

if __name__ == "__main__":
    args = parse_args()
    main(args)