import os
import cv2
import requests
import threading
from datetime import datetime
import config
from utils import logger

class AlertManager:
    """
    Handles saving alert images and sending alerts to the API.
    """
    def __init__(self):
        self.api_url = config.API_URL
        self.headers = config.HEADERS
        self.alert_id = config.ALERT_ID
        self.image_dir = config.ALERT_IMAGE_DIR
        logger.info(f"AlertManager initialized. Saving images to: {self.image_dir}")

    def save_alert_image(self, frame, track_id):
        """
        Saves the current frame as a JPG file.

        Args:
            frame: The video frame to save.
            track_id: The track_id of the person triggering the alert.

        Returns:
            str: The file path where the image was saved, or None on failure.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alert_track_{track_id}_{timestamp}.jpg"
            filepath = os.path.join(self.image_dir, filename)
            
            # Save the image
            cv2.imwrite(filepath, frame)
            
            logger.info(f"Saved alert image to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save alert image for track {track_id}: {e}")
            return None

    def _send_api_alert(self, track_id, elapsed_time, saved_image_path):
        """
        Sends the API request directly (synchronously) as multipart/form-data, 
        matching the curl command.
        """
        try:
            current_timestamp = datetime.now().isoformat()
            
            # 1. Prepare the form data (non-file fields)
            # The API is expecting the values to be strings *containing* quotes.
            form_data = {
                'alerts[id]': f'"{self.alert_id}"',
                'alerts[time]': f'"{current_timestamp}"',
                'alerts[description]': f'"Loitering alert: Track ID {track_id} detected for {elapsed_time:.1f}s from {config.INPUT_SOURCE}."'
            }

            # 2. Open the file and send the request
            with open(saved_image_path, 'rb') as f:
                # 'files' dict tells requests how to structure the file upload
                # (filename, file-object, content-type)
                file_to_upload = {
                    'alerts[image]': (os.path.basename(saved_image_path), f, 'image/jpeg')
                }
                
                logger.info(f"Sending API alert (form-data) to {self.api_url}...")
                logger.debug(f"Form data being sent: {form_data}") # For debugging
                
                # By using 'data' and 'files', requests automatically sets
                # 'Content-Type: multipart/form-data' and handles the boundaries.
                response = requests.post(
                    self.api_url,
                    headers=self.headers, # Auth headers
                    data=form_data,      # Text data
                    files=file_to_upload # File data
                )
            
            # 3. Handle response
            if 200 <= response.status_code < 300:
                logger.info(f"API alert sent successfully. Response: {response.json()}")
            else:
                logger.warning(
                    f"API alert failed. Status: {response.status_code}, Response: {response.text}"
                )
        
        except FileNotFoundError:
            logger.error(f"Image file not found for upload: {saved_image_path}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending API alert: {e}")
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"An unexpected error occurred in alert function: {e}", exc_info=True)


    def trigger_alert(self, frame, track_id, elapsed_time):
        """
        Triggers the full alert process:
        1. Saves an image of the event.
        2. Sends an alert to the API (synchronously).
        """
        logger.warning(
            f"ALERT: Track ID {track_id} exceeded loitering threshold ({elapsed_time:.1f}s)"
        )
        
        # 1. Save the image
        saved_image_path = self.save_alert_image(frame, track_id)
        
        if saved_image_path is None:
            logger.error("Skipping API alert because image save failed.")
            return

        # 2. Send the API alert directly in the main thread
        # This will block execution until the API responds.
        self._send_api_alert(int(track_id), elapsed_time, saved_image_path)

