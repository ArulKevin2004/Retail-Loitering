import os

# --- API Configuration ---
# Your provided API details
API_URL = 'https://virtual-alt-api.surveillant.tech/api/v1/alerts'
API_KEY = '2c3ce52a961b5588525eb26f731c7d94'
HEADERS = {'Authorization': f'API_KEY {API_KEY}'}
ALERT_ID = 'f265b6e4-1faf-4595-82d2-fc1386b6a4d9'

# --- Input Configuration ---
# Use 0 for webcam, or provide a path to a video file or an RTSP URL
# Example RTSP: "rtsp://username:password@192.168.1.10:554/stream"
# Example Video: "videos/people_walking.mp4"
INPUT_SOURCE = "/mnt/7EC84F57C84F0CB9/vishal/Retail_loitering/videos/sample_footage.mp4"#" rtsp://admin:Fuck12345@fordland.dvrlists.com:8554/Streaming/Channels/102""/mnt/7EC84F57C84F0CB9/vishal/Retail_loitering/videos/sample_footage.mp4" # <-- IMPORTANT: SET THIS

# --- Model Configuration ---
# We use yolov8n.pt (nano) for speed. You can use others like yolov8s.pt, yolov8m.pt
YOLO_MODEL_PATH = "yolov8n.pt"
# Tracker configuration file. BoTSORT is recommended.
YOLO_TRACKER_CONFIG = "botsort.yaml"
# Confidence threshold for detection
CONFIDENCE_THRESH = 0.4
# Class ID for 'person' in the COCO dataset is 0
PERSON_CLASS_ID = 0

# --- Loitering Configuration ---
# Time in seconds a person can remain before an alert is triggered
LOITERING_THRESHOLD_SEC = 1

# --- Output Configuration ---
# Directory to save images of alerted individuals
ALERT_IMAGE_DIR = "alert_images"

# Create the alert images directory if it doesn't exist
os.makedirs(ALERT_IMAGE_DIR, exist_ok=True)

# --- Visualization Configuration ---
# Colors (B, G, R)
COLOR_GREEN = (0, 255, 0)
COLOR_ORANGE = (0, 165, 255)
COLOR_RED = (0, 0, 255)

# Time thresholds for color changes (as a fraction of the full threshold)
WARN_THRESHOLD_PERCENT = 0.6 # 60% of the time, change to orange
