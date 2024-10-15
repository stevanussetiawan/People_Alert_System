import cv2
import base64
from ultralytics import YOLO  

def draw_boxes(frame, boxes, confidences, indices):
    """Draw bounding boxes on the frame for detected people."""
    for i in indices:
        x, y, w, h = boxes[i]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"PERSON | {confidences[i]:.2f}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame

def convert_image_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def load_yolo_model(weight_path):
    """Load the pretrained YOLOv8 model from Ultralytics."""
    # Specify the model name 'yolov8' if supported by ultralytics
    return YOLO(weight_path)

def is_video_file(input_path):
    """Check if the input path is a video file."""
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    return input_path.lower().endswith(video_extensions)