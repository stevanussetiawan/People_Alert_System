import argparse
from yolo.yolo_processor import YoloProcessor

def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="YOLO Processor for Video/Images/Webcam")
    parser.add_argument('--path', type=str, required=True, 
                        help="Input path for the video, image, or 'webcam' for live stream")
    parser.add_argument('--weight_path', type=str, required=True, 
                        help="Path to the YOLO model weights (e.g., yolov8n.pt)")
    parser.add_argument('--output_dir', type=str, required=True, 
                        help="Directory to save the output frames")
    parser.add_argument('--n_people', type=int, default=1, 
                        help="Number of people to trigger an alert")

    # Parse the arguments
    args = parser.parse_args()

    # Initialize the video processor
    processor = YoloProcessor(
        input_path=args.path,
        weight_path=args.weight_path,
        output_dir=args.output_dir,
        n_people=args.n_people
    )

    # Start processing
    processor.process()

if __name__ == "__main__":
    main()
    
    # python main.py --path webcam --weight_path models/yolov8n.pt --output_dir output_frames --n_people 1
