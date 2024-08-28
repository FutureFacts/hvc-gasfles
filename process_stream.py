import os
import datetime
import cv2
import torch
import csv
from PIL import Image
# import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from transformers import ViTForImageClassification, ViTImageProcessor
from collections import deque
from dotenv import load_dotenv
import threading
import schedule
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
model = ViTForImageClassification.from_pretrained(
    "checkpoint-220")


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


def send_email(subject, body, to_email, from_email, smtp_server, smtp_port):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(1)  # Enable debug output for the SMTP session
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email sent successfully!")

    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
    except smtplib.SMTPRecipientsRefused as e:
        print(f"SMTP Recipients Refused: {e}")
    except smtplib.SMTPSenderRefused as e:
        print(f"SMTP Sender Refused: {e}")
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def get_timestamp_list(csv_path, day):
    timestamp_list = []
    with open(csv_path, "r") as csvfile:
        a = csvfile.readlines()
    for elem in a:
        if elem.startswith(day):
            timestamp_detection = elem.split(",")[1]
            timestamp_list.append(timestamp_detection)

    return timestamp_list


def compose_email(day):
    timestamp_list = get_timestamp_list("csv/gasfles_counts.csv", day)
    detection_count = len(timestamp_list)

    subject = f"LGC telling Lijn 1,4,5 van {day}"
    body = f"""
    Beste Jeroen,

    Het aantal gedetecteerde gasflessen van {day} is: {detection_count},\nMet de volgende timestamps: \n \n 
    {timestamp_list} \n \n
    Met vriendelijke groet,\n
    Max Druyvesteyn \nFuture Facts\n
    (Deze email is automatisch gegenereerd. Voor vragen kan je mailen naar max.druyvesteyn@futurefacts.nl)
    
    """
    to_email = "xxxx@xxxx.com"  # replace with recipient address
    from_email = "futurefacts@pahvc.org"  # example
    smtp_server = "10.1.55.10"  # hvc server settings
    smtp_port = 25

    send_email(subject, body, to_email, from_email,
               smtp_server, smtp_port)


def job():
    today = datetime.today()
    yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"Running send_email job at {datetime.now(datetime.UTC)}")
    compose_email(yesterday)
    print("email sent succesfully")


# Schedule the job every day
schedule.every().day.at("02:17").do(job)


def process_videostream(video_source, is_stream=True):
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
            date = datetime.now(datetime.UTC).strftime('%Y-%m-%d')
            timeformat = datetime.now(datetime.UTC).strftime('%H:%M:%S')
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
    # Start the process_stream logic
    print('in main')
    print(os.getcwd())
    print(os.environ["STREAM_PATH"])
    video_source = os.environ["STREAM_PATH"]
    if os.environ["INPUT_TYPE"] == "stream":
        is_stream = True
    else:
        is_stream = False
    # Run process_stream in a separate thread
    stream_thread = threading.Thread(
        target=process_videostream, args=(video_source, is_stream))
    stream_thread.start()

    # Keep checking for scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(1)
