import cv2
import configparser
import os
import winsound
import psycopg2
import numpy as np
from database.models import insert_alert_image, insert_alert_video, insert_alert_webcam
from datetime import timedelta, datetime
from yolo.yolo_utils import draw_boxes, convert_image_to_base64, load_yolo_model, is_video_file
from emailing.email_util import send_email_alert_video, send_email_alert_photo, send_email_alert_webcam

class YoloProcessor:
    def __init__(self, input_path, weight_path, output_dir, n_people, conf_threshold=0.3, roi=None):
        """
        Initialize the YOLO video processor with the necessary paths and parameters.
        Supports video, image, and webcam inputs.
        """
        self.input_path = input_path
        self.conf_threshold = conf_threshold
        self.model = load_yolo_model(weight_path)  # Load the pretrained YOLOv10 model
        self.cap = None
        self.output_dir = output_dir
        self.n_people = n_people
        self.roi = roi

        self.config = configparser.ConfigParser()
        self.config.read('emailing/config.ini')

        if input_path != 'webcam':
            name_file, ext = self.input_path.rsplit('.', 1)
            self.save_file = f"{name_file}_evidence.{ext}"

            # Check if the input is a video or image
            if is_video_file(self.input_path):
                self.cap = cv2.VideoCapture(input_path)
                if not self.cap.isOpened():
                    raise FileNotFoundError(f"Could not open video at {self.input_path}")
            elif not os.path.isfile(input_path):
                raise FileNotFoundError(f"Input file not found at {self.input_path}")
        else:
            self.cap = cv2.VideoCapture(0)  # Access the webcam
            
    def add_alert_overlay(self, frame):
        """Add a red translucent overlay and alert text to the frame."""
        overlay = frame.copy()
        height, width = frame.shape[:2]
        # Red translucent overlay
        cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 255), -1)
        frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)  # 40% opacity
        
        # Add alert text
        alert_text = "ALERT: Too many people detected!"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(alert_text, font, 1.5, 2)[0]
        text_x = (width - text_size[0]) // 2
        text_y = (height + text_size[1]) // 2
        cv2.putText(frame, alert_text, (text_x, text_y), font, 1.5, (255, 255, 255), 3, cv2.LINE_AA)
        return frame

    def apply_roi(self, frame):
        """Apply the Region of Interest (ROI) if specified."""
        if self.roi is not None:
            x, y, w, h = self.roi
            return frame[y:y+h, x:x+w]  # Crop the frame to the ROI
        return frame  # Return the full frame if no ROI is defined
            
    def detect_people(self, frame):
        """Detect people in a frame and return their count, indices, boxes, and confidences."""
        
        frame_roi = self.apply_roi(frame)
        results = self.model(frame_roi)  # Run the detection using the model
        boxes, confidences = [], []

        for result in results:
            for detection in result.boxes:
                class_id = int(detection.cls)
                confidence = float(detection.conf)
                if class_id == 0 and confidence > self.conf_threshold:
                    x, y, w, h = detection.xywh[0]  # Coordinates and dimensions
                    boxes.append([int(x - w // 2), int(y - h // 2), int(w), int(h)])
                    confidences.append(confidence)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, 0.3)
        return len(indices), indices.flatten() if len(indices) > 0 else [], boxes, confidences
    
    def save_segments(self, start_time, end_time, fps, save_file, frame_data):
        """Save detected segments to new video files with bounding boxes."""
        # Output video codec and writer for MP4
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'mp4v' codec for MP4 format
        out = cv2.VideoWriter(save_file, fourcc, fps, (int(self.cap.get(3)), int(self.cap.get(4))))

        # Write frames for the current segment using stored detection results
        for frame, boxes, confidences, indices, timestamp in frame_data:
            if start_time <= timestamp <= end_time:
                # Draw bounding boxes on the frame
                frame = draw_boxes(frame, boxes, confidences, indices)
                out.write(frame)
            elif timestamp > end_time:
                break  # Stop writing frames for this segment

        out.release()  # Release the video writer after finishing the segment
        print("Video segments saved successfully.")

    def process_video(self):
        """Process the input video, detect people, and save frames with timestamped filenames."""
        if not self.cap.isOpened():
            raise ValueError("Could not open the video file.")

        fps = self.cap.get(cv2.CAP_PROP_FPS)  # Get frames per second for timestamp calculation
        n_people_start = None  # Track when the threshold is first exceeded
        frame_number = 0
        save_alert_tmp = 'alert_tmp_video.jpg'
        frame_data = []  # To store frames and associated information for alert segments

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("End of video reached or failed to grab frame.")
                break

            frame_number += 1
            timestamp = timedelta(seconds=frame_number / fps)  # Calculate the current timestamp

            # Detect people in the current frame
            people_count, indices, boxes, confidences = self.detect_people(frame)
            frame = draw_boxes(frame, boxes, confidences, indices)
            frame_data.append((frame, boxes, confidences, indices, timestamp))

            # Display the people count in the top-left corner
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = f"People Count: {people_count}"
            text_position = (10, 30)  # (x, y) coordinates for the text position (top-left corner)
            cv2.putText(frame, text, text_position, font, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # If the people count exceeds the threshold (self.n_people)
            if people_count >= self.n_people:
                if n_people_start is None:
                    # Mark when the threshold is first breached
                    n_people_start = timestamp
                    print(f"{self.n_people} or more people detected starting at: {n_people_start}")

                # Calculate the duration since people count exceeded the threshold
                duration = timestamp - n_people_start
                print(f"Duration: {duration}")

                # Trigger alert if the threshold has been breached for more than the specified time (e.g., 5 seconds)
                # if duration > timedelta(seconds=1):
                if duration > timedelta(minutes=2):
                    # Add a red translucent overlay for visual alert
                    overlay = frame.copy()
                    height, width, _ = frame.shape
                    cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 255), -1)  # Red rectangle overlay

                    frame = self.add_alert_overlay(frame)
                    winsound.Beep(1000, 1000)  # Beep for 1 second

                    if not os.path.exists(save_alert_tmp):
                        cv2.imwrite(save_alert_tmp, frame)
                        send_email_alert_video(self.config, self.n_people, n_people_start, timestamp, save_alert_tmp)
                        
                        data = [
                            self.input_path,
                            datetime.now(),
                            n_people_start,
                            timestamp,
                            convert_image_to_base64(save_alert_tmp),
                            self.config['EMAIL']['recipient_email']
                        ]
                        insert_alert_video(data)

            # If people count drops below the threshold, reset the start time
            elif n_people_start is not None:
                print(f"People count dropped below {self.n_people}. Resetting the timer.")
                n_people_start = None
                if os.path.exists(save_alert_tmp):
                    os.remove(save_alert_tmp)

            # Display the frame with detections and alerts
            cv2.imshow("Video Detection", frame)

            # Break loop on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the video capture and close all OpenCV windows
        self.cap.release()
        cv2.destroyAllWindows()
                
    def process_image(self):
        """Process a photo, detect people, and display the result with bounding boxes."""
        # Read the image from the given input path
        image = cv2.imread(self.input_path)
        if image is None:
            raise FileNotFoundError(f"Could not read image at {self.input_path}")

        # Detect people in the image
        people_count, indices, boxes, confidences = self.detect_people(image)

        # Draw bounding boxes around detected people
        image = draw_boxes(image, boxes, confidences, indices)
        image = self.add_alert_overlay(image)

        cv2.imwrite(self.save_file, image)
        print(f"Image saved as: {self.save_file}")
        print(people_count)
        
        # Send an email alert if the number of detected people exceeds the threshold
        if people_count >= self.n_people:
            send_email_alert_photo(self.config, self.n_people, self.save_file)
            data = [
                self.save_file,
                datetime.now(),
                convert_image_to_base64(self.save_file),
                self.config['EMAIL']['recipient_email']
            ]
            insert_alert_image(data)
                
        os.remove(self.save_file)
        
    def process_webcam(self):
        """Process frames from the webcam, trigger alerts if people count exceeds the threshold for more than 1 minute."""
        if not self.cap.isOpened():
            raise ValueError("Could not open the webcam.")

        fps = self.cap.get(cv2.CAP_PROP_FPS)  # Get frames per second for timestamp calculation
        n_people_start = None  # Track when the threshold is first exceeded
        frame_number = 0
        save_alert_tmp = 'alert_tmp.jpg'

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame from webcam.")
                break

            frame_number += 1
            timestamp = timedelta(seconds=frame_number / fps)  # Calculate the current timestamp

            people_count, indices, boxes, confidences = self.detect_people(frame)
            frame = draw_boxes(frame, boxes, confidences, indices)
            
            # Display the people count in the top-left corner
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = f"People Count: {people_count}"
            text_position = (10, 30)  # (x, y) coordinates for the text position (top-left corner)
            cv2.putText(frame, text, text_position, font, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # If the people count exceeds the threshold (self.n_people)
            if people_count >= self.n_people:
                if n_people_start is None:
                    # Mark when the threshold is first breached
                    n_people_start = timestamp
                    print(f"{self.n_people} or more people detected starting at: {n_people_start}")

                # Calculate the duration since people count exceeded the threshold
                duration = timestamp - n_people_start

                print('the duration time: ', duration)
                if duration > timedelta(minutes=2):
                # if duration > timedelta(seconds=5):
                    # Add a red translucent overlay for visual alert
                    frame = self.add_alert_overlay(frame)
                    winsound.Beep(1000, 1000)  # Beep for 1 second

                    if not os.path.exists(save_alert_tmp):
                        cv2.imwrite(save_alert_tmp, frame)
                        send_email_alert_webcam(self.config, self.n_people, save_alert_tmp, n_people_start, timestamp)
                        data = [
                            datetime.now(),
                            n_people_start,
                            timestamp,
                            convert_image_to_base64(save_alert_tmp),
                            self.config['EMAIL']['recipient_email']
                        ]
                        insert_alert_webcam(data)
            
            # If people count drops below the threshold, reset the start time
            elif n_people_start is not None:
                print(f"People count dropped below {self.n_people}. Resetting the timer.")
                n_people_start = None
                if os.path.exists(save_alert_tmp):
                    os.remove(save_alert_tmp)
                

            # Display the frame with detections and alerts
            cv2.imshow("Webcam Detection", frame)

            # Break loop on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the webcam and close all OpenCV windows
        self.cap.release()
        cv2.destroyAllWindows()

    def process(self):
        """Automatically determine whether to process video, image, or webcam based on the input."""
        if self.input_path == 'webcam':
            print("Processing webcam feed...")
            self.process_webcam()
        elif is_video_file(self.input_path):
            print("Processing video...")
            self.process_video()
        else:
            print("Processing image...")
            self.process_image()