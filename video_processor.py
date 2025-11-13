import cv2
import queue
import threading
import time
import config
from utils import logger

class VideoProcessor:
    """
    Handles reading the video stream in a separate thread,
    running inference, and coordinating all modules.
    """
    def __init__(self, detector, tracker, alert_manager, visualizer_func):
        self.detector = detector
        self.tracker = tracker
        self.alert_manager = alert_manager
        self.visualizer_func = visualizer_func
        
        self.input_source = config.INPUT_SOURCE
        self.cap = cv2.VideoCapture(self.input_source)
        
        if not self.cap.isOpened():
            logger.error(f"Failed to open video source: {self.input_source}")
            raise IOError(f"Cannot open video source: {self.input_source}")

        # A queue to hold frames read from the video thread
        # This prevents the main thread from blocking on I/O
        self.frame_queue = queue.Queue(maxsize=10)
        
        # Flag to control the running state of threads
        self.running = True
        
        # The thread that reads frames
        self.reader_thread = threading.Thread(target=self._reader_thread, daemon=True)

    def _reader_thread(self):
        """
        Private method to be run in its own thread.
        Continuously reads frames from the video source and puts them in a queue.
        """
        logger.info("Reader thread started...")
        while self.running:
            if not self.frame_queue.full():
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("End of video stream or read error.")
                    self.running = False
                    break
                self.frame_queue.put(frame)
            else:
                # If queue is full, wait briefly to avoid busy-waiting
                time.sleep(0.01)
        
        logger.info("Reader thread stopped.")

    def start(self):
        """Starts the video reader thread."""
        self.reader_thread.start()

    def run_inference(self):
        """
        Runs the main inference loop.
        Gets frames from the queue, processes them, and displays the result.
        """
        logger.info("Inference loop starting...")
        while self.running:
            try:
                # Get a frame from the queue, blocking if empty
                frame = self.frame_queue.get(timeout=10) # 10-second timeout
            except queue.Empty:
                logger.warning("Frame queue is empty. Is the video source still active?")
                # If the reader thread has stopped, we should too
                if not self.reader_thread.is_alive():
                    self.running = False
                continue

            # 1. Detect and Track
            results = self.detector.detect_and_track(frame)
            if results is None:
                continue

            # 2. Update Loitering Timers
            current_track_ids = []
            if results.boxes.id is not None:
                # Convert tensor to numpy array of ints
                current_track_ids = results.boxes.id.cpu().numpy().astype(int)
            
            loitering_data = self.tracker.update(current_track_ids)
            
            # 3. Check for Alerts
            for track_id, data in loitering_data.items():
                if (data['status'] == 'alert' and 
                    not self.tracker.has_been_alerted(track_id)):
                    
                    # Mark as alerted to prevent spam
                    self.tracker.mark_alerted(track_id)
                    
                    # Trigger the alert (saves image, sends API call in new thread)
                    self.alert_manager.trigger_alert(frame, track_id, data['elapsed'])

            # 4. Visualize
            annotated_frame = self.visualizer_func(frame, results, loitering_data)
            
            # 5. Display
            cv2.imshow("Loitering Detection", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("'q' pressed. Stopping application.")
                self.running = False
                break
        
        logger.info("Inference loop stopped.")

    def cleanup(self):
        """Stops threads and releases resources."""
        logger.info("Cleaning up resources...")
        self.running = False
        if self.reader_thread.is_alive():
            self.reader_thread.join(timeout=1)
        self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Cleanup complete.")
