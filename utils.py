# import os
# os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

from moviepy.editor import VideoFileClip
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


def create_short_video(input_video, output_video, start_time):
    # Load the input video clip
    video_clip = VideoFileClip(input_video)

    # Set the end time based on the start time and duration (2 minutes)
    end_time = start_time + 120  # 2 minutes in seconds

    # Extract the subclip starting from the specified start time and lasting for 2 minutes
    subclip = video_clip.subclip(start_time, end_time)

    # Write the subclip to a new video file
    subclip.write_videofile(output_video, codec="libx264", audio_codec="aac")

    # Close the original video clip
    video_clip.close()


def count_detections(csv_file):
    df = pd.read_csv(csv_file, sep=",", names=[
                     'date', 'time', 'count'], header=None)
    today = "2024-06-11"
    daily_detections = df[df['date'] == today]
    detection_count = len(daily_detections)
    return daily_detections, today


def compose_mail_body(date):
    csv_file = 'csv/gasfles_counts.csv'  # Update with your CSV file path
    detections, date = count_detections(csv_file)
    detection_count = detections.shape[0]
    timestamp_list = list(detections["time"])
    formatted_timestamps = "\n".join(timestamp_list)
    subject = f"LGC telling Lijn 1,4,5 van {date}"
    body = f"""
    Beste Jeroen,

    Het aantal gedetecteerde gasflessen van {date} is: {detection_count},
    Met de volgende timestamps:

    {formatted_timestamps}

    Met vriendelijke groet,
    Max Druyvesteyn
    Future Facts
    (Deze email is automatisch gegenereerd. Voor vragen kan je mailen naar max.druyvesteyn@futurefacts.nl)
    """
    # Replace with recipient's email address
    to_email = ["max.druyvesteyn@futurefacts.nl", "maxdruyvesteyn@hotmail.com"]
    from_email = "xxx@xxx.com"  # Replace with your address
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "xxx@gmail.com"  # Replace with your Gmail address
    # create your passcode for your gmail address
    smtp_password = "xxxx xxxx xxxx xxx"

    send_email(subject, body, to_email, from_email,
               smtp_server, smtp_port, smtp_user, smtp_password)


def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ', '.join(to_email)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Example usage
input_video_path = "archive/C133 - Obstakelbeveiliging Lijn 1-4-2024-07-09_00h00min00s000ms.mp4"
output_video_path = "short_video.mp4"
start_time_seconds = 2160  # Start time in seconds

create_short_video(input_video_path, output_video_path, start_time_seconds)
