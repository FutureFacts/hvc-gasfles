import os
import datetime
import cv2
import torch
import csv
from PIL import Image
from transformers import ViTForImageClassification, ViTImageProcessor
from collections import deque
from dotenv import load_dotenv
import threading
import time

load_dotenv(override=True)

model_name_or_path = "myvitprocessor"
processor = ViTImageProcessor.from_pretrained(model_name_or_path)

# Define the directory to save "gasfles" images
gasfles_dir = "data/detected_gasfles"
false_neg_dir = "data/false_negatives_potentially"
false_pos_dir = "data/false_positives_potentially"
os.makedirs(gasfles_dir, exist_ok=True)
os.makedirs(false_neg_dir, exist_ok=True)
os.makedirs(false_pos_dir, exist_ok=True)

# Load the model using the `from_pretrained()` method
model = ViTForImageClassification.from_pretrained("trainset2")

# model.eval()


def get_timestamp(frame_count, fps):
    total_seconds = frame_count / fps
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Function to write results to CSV


def write_results_to_csv(date, time, count, filename):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, time, count])


def main(video_source, is_stream=True):
    global gasfles_count

    # Open the video stream or file
    cap = cv2.VideoCapture(video_source)

    # Check if the video source is opened successfully
    if not cap.isOpened():
        print(
            f"Error: Could not open {'video stream' if is_stream else 'video file'}.")
        return

    # Get video properties
    # Default to 50 FPS if reading from a file
    fps = cap.get(cv2.CAP_PROP_FPS) if is_stream else 50
    frame_interval = int(fps * 1)  # Frame interval for 1 second

    # Initialize counters
    frame_count = 0
    gasfles_count = 0
    prediction_interval = fps
    last_detection_framecount = 0

    # Sliding window to store predictions and frames
    predictions_window = deque(maxlen=6)
    frames_window = deque(maxlen=6)
    framecount_window = deque(maxlen=6)

    # Start end-of-day routine in a separate thread
    # threading.Thread(target=end_of_day_routine, daemon=True).start()
    print("starting stream processing")
    while True:
        ret, frame = cap.read()
        if not ret:
            if is_stream:
                continue  # If frame is not read properly, skip this iteration for streams
            else:
                break  # End loop for video files

        # Process every 1 second
        if frame_count % frame_interval == 0:
            current_timestamp = get_timestamp(frame_count, fps)
            # Convert the frame to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Apply the transformations
            input_tensor = processor(images=pil_image, return_tensors="pt")

            # Classify the frame
            with torch.no_grad():
                outputs = model(**input_tensor)
                predicted = torch.argmax(outputs.logits, dim=1).item()

            print(frame_count, predicted)
            # Append prediction and frame to sliding window
            predictions_window.append(predicted)
            frames_window.append(frame)
            framecount_window.append(frame_count)
            date = datetime.datetime.now().strftime('%Y-%m-%d')
            timeformat = datetime.datetime.now().strftime('%H:%M:%S')
            if len(predictions_window) == 6 * frame_interval // prediction_interval:
                count_of_ones = sum(predictions_window)

                if count_of_ones == 4:
                    if frame_count - last_detection_framecount > 4 * fps:
                        # Save frames in the current window
                        for i, f in enumerate(frames_window):
                            current_timestamp = get_timestamp(
                                framecount_window[i], fps)
                            if predictions_window[i] == 1:
                                frame_filename = os.path.join(
                                    gasfles_dir, f"gasfles1_{gasfles_count}_{timeformat}_{framecount_window[i]}.png")
                                print("saved gasfles")
                                cv2.imwrite(frame_filename, f)
                            else:
                                frame_filename = os.path.join(
                                    false_neg_dir, f"gasfles1_{gasfles_count}_{timeformat}_{framecount_window[i]}.png")
                                cv2.imwrite(frame_filename, f)
                                print("saved false_negative")
                        gasfles_count += 1
                        write_results_to_csv(date,
                                             timeformat,
                                             1,
                                             "csv/gasfles_counts.csv")
                        last_detection_framecount = frame_count

                elif count_of_ones > 4 and predictions_window[-1] == 1:
                    frame_filename = os.path.join(
                        gasfles_dir, f"gasfles1_{gasfles_count}_{timeformat}_{frame_count}.png")
                    cv2.imwrite(frame_filename, frame)
                    last_detection_framecount = frame_count

                elif count_of_ones == 1 and frame_count - last_detection_framecount > 4 * fps and predictions_window[0] == 1 and gasfles_count > 0:
                    frame_filename = os.path.join(
                        false_pos_dir, f"gasfles1_{gasfles_count}_{timeformat}.png")
                    cv2.imwrite(frame_filename, frame)
                    print("saved false positive")
                    last_detection_framecount = frame_count

        frame_count += 1

    # Release the video capture object
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # For testing with a video stream:
    print('in main')
    print(os.getcwd())
    print(os.environ["STREAM_PATH"])
    video_source = os.environ["STREAM_PATH"]
    if os.environ["INPUT_TYPE"] == "stream":
        is_stream = True
    else:
        is_stream = False
    print(is_stream)

    main(video_source, is_stream)
