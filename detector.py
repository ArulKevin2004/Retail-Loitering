from ultralytics import YOLO
import config
from utils import logger

class ObjectDetector:
    """
    Handles object detection and tracking using the YOLO model.
    """
    def __init__(self):
        try:
            self.model = YOLO(config.YOLO_MODEL_PATH)
            logger.info(f"Successfully loaded YOLO model from {config.YOLO_MODEL_PATH}")
        except Exception as e:
            logger.error(f"Error loading YOLO model: {e}")
            raise

    def detect_and_track(self, frame):
        """
        Performs object detection and tracking on a single frame.

        Args:
            frame: The input video frame.

        Returns:
            The results object from the YOLO model, containing detection
            and tracking information.
        """
        try:
            # We track only the 'person' class
            results = self.model.track(
                frame,
                persist=True,
                tracker=config.YOLO_TRACKER_CONFIG,
                classes=[config.PERSON_CLASS_ID],
                conf=config.CONFIDENCE_THRESH,
                verbose=False # Suppress console output from YOLO
            )
            # Return the first (and only) result object
            return results[0]
        except Exception as e:
            logger.error(f"Error during detection/tracking: {e}")
            return None
